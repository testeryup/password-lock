# main.py
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import json
import asyncio
import threading
from EmulatorGUI import GPIO
from state_manager import StateManager, DoorState
from services.door_service import DoorService
from services.auth_service import AuthService
from services.log_service import LogService
from config import GPIO_CONFIG, SYSTEM_CONFIG
import app_gui

# Khởi tạo FastAPI
app = FastAPI()

# Cấu hình template + static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Khởi tạo State Manager
state_manager = StateManager()
state_manager.correct_password = SYSTEM_CONFIG["PASSWORD"]

# Khởi tạo các service
door_service = DoorService(
    state_manager=state_manager,
    relay_pin=GPIO_CONFIG["RELAY_PIN"],
    led_locked_pin=GPIO_CONFIG["LED_LOCKED"],
    led_unlocked_pin=GPIO_CONFIG["LED_UNLOCKED"],
    buzzer_pin=GPIO_CONFIG["BUZZER_PIN"],
    reed_pin=GPIO_CONFIG["REED_PIN"]
)

auth_service = AuthService(
    state_manager=state_manager,
    door_service=door_service
)

log_service = LogService(
    state_manager=state_manager,
    log_file=SYSTEM_CONFIG["LOG_FILE"]
)

# Cấu hình GPIO giả lập
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Thiết lập GPIO
GPIO.setup(GPIO_CONFIG["LED_LOCKED"], GPIO.OUT)
GPIO.setup(GPIO_CONFIG["LED_UNLOCKED"], GPIO.OUT)
GPIO.setup(GPIO_CONFIG["RELAY_PIN"], GPIO.OUT)
GPIO.setup(GPIO_CONFIG["BUZZER_PIN"], GPIO.OUT)
GPIO.setup(GPIO_CONFIG["REED_PIN"], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Mặc định cửa khoá
GPIO.output(GPIO_CONFIG["LED_LOCKED"], GPIO.HIGH)
GPIO.output(GPIO_CONFIG["LED_UNLOCKED"], GPIO.LOW)
GPIO.output(GPIO_CONFIG["RELAY_PIN"], GPIO.LOW)
GPIO.output(GPIO_CONFIG["BUZZER_PIN"], GPIO.LOW)

# WebSocket clients
websocket_clients = []

# Observer để cập nhật WebSocket
class WebObserver:
    def __init__(self):
        self.needs_update = False
        
    async def update(self):
        state_data = state_manager.get_state_json()
        for client in websocket_clients.copy():
            try:
                await client.send_json(state_data)
            except:
                if client in websocket_clients:
                    websocket_clients.remove(client)

# Đăng ký observer
web_observer = WebObserver()
state_manager.add_observer(web_observer)

# WebSocket để cập nhật trạng thái realtime
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        while True:
            # Gửi cập nhật trạng thái
            if hasattr(web_observer, 'needs_update') and web_observer.needs_update:
                await web_observer.update()
                web_observer.needs_update = False
            else:
                await websocket.send_json(state_manager.get_state_json())
                
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
async def get_status():
    return {"status": state_manager.door_state}

@app.post("/unlock")
async def unlock_door(password: str = Form(...)):
    # Sử dụng service xác thực
    result = auth_service.verify_password(password)
    
    # Ghi log
    if result["status"] == "success":
        log_service.log_entry("Mở khoá cửa", "Mở khoá từ Web App")
    
    return result

@app.post("/lock")
async def lock_door():
    # Khoá cửa
    door_service.lock_door()
    
    # Ghi log
    log_service.log_entry("Khoá cửa", "Khoá từ Web App")
    
    return {"status": "success", "message": "Cửa đã khoá!"}

@app.get("/logs")
async def get_logs(limit: int = 10):
    logs = log_service.get_recent_logs(limit)
    return {"logs": logs}

# Khởi chạy giám sát cửa
door_monitor_thread = threading.Thread(target=door_service.monitor_door_state, daemon=True)
door_monitor_thread.start()

# Khởi chạy GUI giả lập trong luồng riêng
def start_gui_app():
    gui = app_gui.DoorLockApp()
    gui.run()

# Chỉ chạy GUI nếu được chạy trực tiếp (không qua uvicorn)
if __name__ == "__main__":
    gui_thread = threading.Thread(target=start_gui_app, daemon=True)
    gui_thread.start()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SYSTEM_CONFIG["WEB_PORT"])

# Thêm sự kiện khi ứng dụng đóng để dọn dẹp GPIO
@app.on_event("shutdown")
def cleanup():
    log_service.log_entry("Hệ thống", "Tắt hệ thống")
    GPIO.cleanup()
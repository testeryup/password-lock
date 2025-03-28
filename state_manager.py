# state_manager.py
import threading
from datetime import datetime
import json
import asyncio
class DoorState:
    LOCKED = "locked"
    UNLOCKED = "unlocked"

class StateManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        # Trạng thái cửa
        self.door_state = DoorState.LOCKED
        self.door_physically_open = False
        
        # Trạng thái màn hình LCD
        self.lcd_text = ["ULock", "Nhập mã..."]
        
        # Theo dõi mật khẩu
        self.wrong_attempts = 0
        self.last_attempt_time = datetime.now()
        self.correct_password = "1234"
        
        # Lịch sử hoạt động
        self.access_log = []
        
        # Danh sách observers
        self.observers = []
    
    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            # Kiểm tra nếu observer là WebObserver
            if hasattr(observer, 'update'):
                if asyncio.iscoroutinefunction(observer.update):
                    # Ghi nhận cần cập nhật, không gọi trực tiếp
                    observer.needs_update = True
                else:
                    # Observer thông thường, gọi ngay
                    observer.update()
    
    def unlock_door(self):
        self.door_state = DoorState.UNLOCKED
        self.log_action("Cửa đã mở khoá")
        self.notify_observers()
    
    def lock_door(self):
        self.door_state = DoorState.LOCKED
        self.log_action("Cửa đã khoá")
        self.notify_observers()
    
    def set_lcd_text(self, line1, line2=""):
        self.lcd_text = [line1, line2]
        self.notify_observers()
    
    def set_door_physical_state(self, is_open):
        self.door_physically_open = is_open
        if is_open:
            self.log_action("Cửa đang mở")
        else:
            self.log_action("Cửa đã đóng")
        self.notify_observers()
    
    def log_action(self, action):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action
        }
        self.access_log.append(log_entry)
    
    def increment_wrong_attempt(self):
        self.wrong_attempts += 1
        self.last_attempt_time = datetime.now()
        self.log_action(f"Nhập mã sai lần {self.wrong_attempts}")
        self.notify_observers()
    
    def reset_wrong_attempts(self):
        self.wrong_attempts = 0
        self.notify_observers()
    
    def check_password(self, password):
        print(f"check password: {password}, correct password: {self.correct_password}")
        return password == self.correct_password
    
    def get_state_json(self):
        return {
            "door_state": self.door_state,
            "door_physically_open": self.door_physically_open,
            "lcd_text": self.lcd_text,
            "wrong_attempts": self.wrong_attempts,
            "logs": self.access_log[-10:] if self.access_log else []
        }
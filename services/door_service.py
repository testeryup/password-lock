# services/door_service.py
import threading
import time
import asyncio
from EmulatorGUI import GPIO
from state_manager import StateManager, DoorState

class DoorService:
    def __init__(self, state_manager=None, 
                 relay_pin=5, led_locked_pin=17, led_unlocked_pin=27, 
                 buzzer_pin=22, reed_pin=4):
        self.state_manager = state_manager or StateManager()
        self.relay_pin = relay_pin
        self.led_locked_pin = led_locked_pin
        self.led_unlocked_pin = led_unlocked_pin
        self.buzzer_pin = buzzer_pin
        self.reed_pin = reed_pin
        
        # Buzzer component reference (will be set by the app)
        self.buzzer_component = None
        
        # Timers
        self.auto_lock_timer = None
    
    def set_buzzer_component(self, buzzer):
        """Set the Buzzer component reference"""
        self.buzzer_component = buzzer
    
    def unlock_door(self, auto_lock_seconds=20):
        """Mở khoá cửa"""
        # Cập nhật GPIO
        GPIO.output(self.relay_pin, GPIO.HIGH)  # Kích hoạt relay
        GPIO.output(self.led_locked_pin, GPIO.LOW)  # Tắt đèn đỏ
        GPIO.output(self.led_unlocked_pin, GPIO.HIGH)  # Bật đèn xanh
        
        # Cập nhật trạng thái
        self.state_manager.door_state = DoorState.UNLOCKED
        self.state_manager.set_lcd_text("Da mo khoa", "Tu dong khoa: " + str(auto_lock_seconds) + "s")
        
        # Mở khóa cũng đồng thời mở cửa trong giả lập
        self.state_manager.door_physically_open = True
        
        # Tạo timer tự động khoá
        if self.auto_lock_timer:
            self.auto_lock_timer.cancel()
        
        # Tự động đóng cửa và khóa sau auto_lock_seconds
        def auto_close_and_lock():
            self.state_manager.set_door_physical_state(False)  # Đóng cửa trước
            self.state_manager.set_lcd_text("Đang đóng...", "Tự động khóa")
            time.sleep(1)  # Delay 1 giây để giả lập quá trình đóng cửa
            self.lock_door()  # Sau khi đóng cửa, thực hiện khóa
        
        self.auto_lock_timer = threading.Timer(auto_lock_seconds, auto_close_and_lock)
        self.auto_lock_timer.daemon = True
        self.auto_lock_timer.start()
        
        # Thông báo đến observers
        self.state_manager.notify_observers()
        
    def lock_door(self):
        """Khoá cửa lại"""
        # Chỉ khóa cửa khi cửa đã đóng
        if not self.state_manager.door_physically_open:
            # Cập nhật GPIO
            GPIO.output(self.relay_pin, GPIO.LOW)  # Ngắt relay
            GPIO.output(self.led_locked_pin, GPIO.HIGH)  # Bật đèn đỏ
            GPIO.output(self.led_unlocked_pin, GPIO.LOW)  # Tắt đèn xanh
            
            # Cập nhật trạng thái
            self.state_manager.door_state = DoorState.LOCKED
            self.state_manager.set_lcd_text("Cua da khoa", "Nhap ma de mo...")
            
            # Hủy timer tự động khoá nếu có
            if self.auto_lock_timer:
                self.auto_lock_timer.cancel()
                self.auto_lock_timer = None
            
            # Thông báo đến observers
            self.state_manager.notify_observers()
        else:
            # Cảnh báo cần đóng cửa trước
            self.state_manager.set_lcd_text("Canh bao!", "Dong cua truoc")
            self.activate_buzzer(1)
    
    def activate_buzzer(self, duration=3):
        """Kích hoạt còi báo động"""
        # Sử dụng buzzer component nếu có
        if self.buzzer_component:
            self.buzzer_component.start_buzz(duration)
        else:
            # Fallback to direct GPIO if component isn't set
            GPIO.output(self.buzzer_pin, GPIO.HIGH)
            # Tạo timer để tắt buzzer
            threading.Timer(duration, lambda: GPIO.output(self.buzzer_pin, GPIO.LOW)).start()
    
    def monitor_door_state(self):
        """Giám sát trạng thái vật lý của cửa (đóng/mở)"""
        while True:
            # Trong môi trường giả lập, chúng ta có thể bỏ qua việc đọc từ GPIO trực tiếp
            # và chỉ dựa vào trạng thái trong state_manager
            door_open = self.state_manager.door_physically_open
            
            # Xử lý cảnh báo hoặc tự động khóa
            # Cập nhật trạng thái cửa nếu có thay đổi
            if self.state_manager.door_physically_open != door_open:
                self.state_manager.set_door_physical_state(door_open)
                
                # Nếu cửa đang mở khoá và cửa đã đóng, tự động khoá lại
                if door_open == False and self.state_manager.door_state == DoorState.UNLOCKED:
                    self.lock_door()
                
                # Nếu cửa đang mở (vật lý) nhưng đã khoá, kích hoạt cảnh báo
                if door_open == True and self.state_manager.door_state == DoorState.LOCKED:
                    self.state_manager.set_lcd_text("Canh bao!", "Cua dang mo")
                    self.activate_buzzer(5)
            
            time.sleep(0.5)  # Kiểm tra mỗi 500ms
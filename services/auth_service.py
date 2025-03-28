# services/auth_service.py
from datetime import datetime
import time
from state_manager import StateManager
from services.door_service import DoorService

class AuthService:
    def __init__(self, state_manager=None, door_service=None):
        self.state_manager = state_manager or StateManager()
        self.door_service = door_service or DoorService(state_manager)
        
        # Số giây chờ sau khi nhập sai mật khẩu quá nhiều lần
        self.lockout_timeout = 30
    
    def verify_password(self, password):
        """Kiểm tra tính hợp lệ của mật khẩu và xử lý đăng nhập"""
        print("check password:", password)
        print("check self:", self)
        current_time = time.time()
        last_attempt_time = self.state_manager.last_attempt_time.timestamp()
        
        # Kiểm tra nếu đã hết thời gian lockout
        if (current_time - last_attempt_time) > self.lockout_timeout:
            self.state_manager.reset_wrong_attempts()
        
        # Kiểm tra nếu đã bị khoá do nhập sai quá nhiều lần
        if self.state_manager.wrong_attempts >= 3:
            self.door_service.activate_buzzer(2)
            remaining_seconds = int(self.lockout_timeout - (current_time - last_attempt_time))
            
            if remaining_seconds > 0:
                self.state_manager.set_lcd_text("Qua nhieu lan thu", f"Cho {remaining_seconds}s")
                return {
                    "status": "error",
                    "message": f"Vui lòng thử lại sau {remaining_seconds} giây",
                    "remaining_time": remaining_seconds
                }
            else:
                self.state_manager.reset_wrong_attempts()
        
        # Kiểm tra mật khẩu
        if self.state_manager.check_password(password):
            # Mật khẩu đúng
            self.state_manager.reset_wrong_attempts()
            self.door_service.unlock_door()
            
            return {
                "status": "success", 
                "message": "Cửa đã mở khoá!"
            }
        else:
            # Mật khẩu sai
            self.state_manager.increment_wrong_attempt()
            remaining_attempts = 3 - self.state_manager.wrong_attempts
            
            if remaining_attempts <= 0:
                # Kích hoạt cảnh báo
                self.door_service.activate_buzzer(3)
                self.state_manager.set_lcd_text("Sai mat khau", "Tam khoa 30s")
                
                return {
                    "status": "error", 
                    "message": "Đã khoá do nhập sai nhiều lần!"
                }
            else:
                self.state_manager.set_lcd_text(f"Sai mat khau!", f"Con {remaining_attempts} lan thu")
                
                return {
                    "status": "error", 
                    "message": f"Sai mật khẩu! Còn {remaining_attempts} lần thử"
                }
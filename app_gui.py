# app_gui.py
import pygame
import pygame.freetype
import sys
import threading
import time
from EmulatorGUI import GPIO
from state_manager import StateManager, DoorState
from components.keypad import Keypad
from components.lcd import LCD
from components.solenoid import SolenoidLock
from components.reed_switch import ReedSwitch
from components.buzzer import Buzzer
from components.led import LED
from components.relay import Relay
from services.door_service import DoorService
from services.auth_service import AuthService
from services.log_service import LogService
from config import GPIO_CONFIG, SYSTEM_CONFIG, UI_CONFIG

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
class DoorLockApp:
    def __init__(self):
        # Khởi tạo pygame
        pygame.init()
        pygame.freetype.init()

        try:
            self.font = pygame.freetype.Font("fonts/Roboto-Regular.ttf", 18)
            self.use_freetype = True
        except FileNotFoundError:
            print("Không tìm thấy font Roboto, đang tải từ internet...")
            self.download_font()
            try:
                self.font = pygame.freetype.Font("fonts/Roboto-Regular.ttf", 18)
                self.use_freetype = True
            except:
                print("Không thể tải font. Sử dụng font mặc định.")
                self.font = pygame.font.SysFont('Arial', 18)
                self.use_freetype = False

        pygame.display.set_caption(UI_CONFIG["APP_TITLE"])
        self.screen = pygame.display.set_mode((UI_CONFIG["APP_WIDTH"], UI_CONFIG["APP_HEIGHT"]))
        self.clock = pygame.time.Clock()
        
        
        # Khởi tạo state manager
        self.state_manager = StateManager()
        self.state_manager.correct_password = SYSTEM_CONFIG["PASSWORD"]
        
        # Khởi tạo các thành phần
        self.setup_components()
        
        # Khởi tạo các service
        self.door_service = DoorService(
            state_manager=self.state_manager,
            relay_pin=GPIO_CONFIG["RELAY_PIN"],
            led_locked_pin=GPIO_CONFIG["LED_LOCKED"],
            led_unlocked_pin=GPIO_CONFIG["LED_UNLOCKED"],
            buzzer_pin=GPIO_CONFIG["BUZZER_PIN"],
            reed_pin=GPIO_CONFIG["REED_PIN"]
        )
        
        # Connect the buzzer to door_service
        self.door_service.set_buzzer_component(self.buzzer)
        
        self.auth_service = AuthService(
            state_manager=self.state_manager,
            door_service=self.door_service
        )
        
        self.log_service = LogService(
            state_manager=self.state_manager,
            log_file=SYSTEM_CONFIG["LOG_FILE"]
        )
        
        # Đăng ký UI observer
        self.state_manager.add_observer(self)
        
        # Khởi động giám sát cửa
        door_monitor_thread = threading.Thread(target=self.door_service.monitor_door_state, daemon=True)
        door_monitor_thread.start()
        
        # Log khởi động
        self.log_service.log_entry("Hệ thống khởi động", "Khởi tạo giao diện Pygame")
    
    def setup_components(self):
        """Thiết lập các thành phần giao diện"""
        
        # LCD hiển thị
        self.lcd = LCD(50, 50, 300, 80)
        
        # Keypad nhập mã
        self.keypad = Keypad(50, 150, 200, 250)
        self.keypad.set_callback(self.process_keypad_input)
        
        # Đèn LED
        self.led_locked = LED(GPIO_CONFIG["LED_LOCKED"], 400, 80, color=(255, 0, 0))
        self.led_unlocked = LED(GPIO_CONFIG["LED_UNLOCKED"], 450, 80, color=(0, 255, 0))
        
        # Relay điều khiển khoá
        self.relay = Relay(GPIO_CONFIG["RELAY_PIN"], 520, 80)
        
        # Khoá solenoid
        self.solenoid = SolenoidLock(
            GPIO_CONFIG["RELAY_PIN"], 
            GPIO_CONFIG["LED_LOCKED"], 
            GPIO_CONFIG["LED_UNLOCKED"], 
            400, 150, 100, 150
        )
        
        # Reed switch (cảm biến cửa)
        self.reed_switch = ReedSwitch(GPIO_CONFIG["REED_PIN"], 550, 350, 100, 80)
        
        # Buzzer
        self.buzzer = Buzzer(GPIO_CONFIG["BUZZER_PIN"], 650, 200, 20)
        
        # Nút điều khiển
        self.buttons = {
            "unlock": pygame.Rect(400, 500, 120, 40),
            "lock": pygame.Rect(600, 500, 120, 40),
            "toggle_door": pygame.Rect(400, 500, 150, 40)
        }
    
    def update(self):
        """Được gọi khi trạng thái thay đổi (observer pattern)"""
        # Cập nhật LCD
        self.lcd.set_text(self.state_manager.lcd_text)
        
        # Cập nhật đèn LED
        if self.state_manager.door_state == DoorState.LOCKED:
            self.led_locked.set_state(GPIO.HIGH)
            self.led_unlocked.set_state(GPIO.LOW)
        else:
            self.led_locked.set_state(GPIO.LOW)
            self.led_unlocked.set_state(GPIO.HIGH)
        
        # Cập nhật khoá
        if self.state_manager.door_state == DoorState.LOCKED:
            self.solenoid.lock()
            self.relay.set_state(GPIO.LOW)
        else:
            self.solenoid.unlock()
            self.relay.set_state(GPIO.HIGH)
        
        # Cập nhật Reed Switch
        self.reed_switch.set_door_open(self.state_manager.door_physically_open)
    
    def process_keypad_input(self, code):
        """Xử lý mã nhập từ keypad"""
        self.lcd.set_text("Đang kiểm tra", "Mã: " + "*" * len(code))
        result = self.auth_service.verify_password(code)
        
        # Log kết quả
        if result["status"] == "success":
            self.log_service.log_entry("Nhập mã đúng", f"Đã mở khoá cửa")
            # KHÔNG cần mở cửa ở đây vì đã được mở trong auth_service
        else:
            self.log_service.log_entry("Nhập mã sai", f"Còn lại {3 - self.state_manager.wrong_attempts} lần thử")
            # Hiển thị thông báo lỗi trên LCD
            self.lcd.set_text("Mã sai!", f"Còn {3 - self.state_manager.wrong_attempts} lần thử")
    
    def draw(self):
        """Vẽ giao diện"""
        # Xóa màn hình
        self.screen.fill(UI_CONFIG["APP_BG_COLOR"])
        
        # Vẽ tiêu đề
        if self.use_freetype:
            text_surface, text_rect = self.font.render("ULock", (0, 0, 0))
            text_rect.centerx = UI_CONFIG["APP_WIDTH"] // 2
            text_rect.top = 10
            self.screen.blit(text_surface, text_rect)
        else:
            title = self.font.render("ULock", True, (0, 0, 0))
            self.screen.blit(title, (UI_CONFIG["APP_WIDTH"] // 2 - title.get_width() // 2, 10))
        
        # Vẽ các thành phần
        self.lcd.draw(self.screen)
        self.keypad.draw(self.screen)
        self.led_locked.draw(self.screen)
        self.led_unlocked.draw(self.screen)
        self.relay.draw(self.screen)
        self.solenoid.draw(self.screen)
        self.reed_switch.draw(self.screen)
        self.buzzer.draw(self.screen)
        
        # Vẽ nút bấm
        # pygame.draw.rect(self.screen, (0, 180, 0), self.buttons["unlock"], border_radius=5)
        # if self.use_freetype:
        #     text_surface, text_rect = self.font.render("MỞ KHOÁ", (255, 255, 255))
        #     text_rect.center = self.buttons["unlock"].center
        #     self.screen.blit(text_surface, text_rect)
        # else:
        #     unlock_text = self.font.render("MỞ KHOÁ", True, (255, 255, 255))
        #     self.screen.blit(unlock_text, (self.buttons["unlock"].centerx - unlock_text.get_width() // 2, 
        #                                   self.buttons["unlock"].centery - unlock_text.get_height() // 2))
        
        pygame.draw.rect(self.screen, (180, 0, 0), self.buttons["lock"], border_radius=5)
        if self.use_freetype:
            text_surface, text_rect = self.font.render("KHOÁ", (255, 255, 255))
            text_rect.center = self.buttons["lock"].center
            self.screen.blit(text_surface, text_rect)
        else:
            lock_text = self.font.render("KHOÁ", True, (255, 255, 255))
            self.screen.blit(lock_text, (self.buttons["lock"].centerx - lock_text.get_width() // 2,
                                       self.buttons["lock"].centery - lock_text.get_height() // 2))
        
        # Vẽ trạng thái
        status = f"Trạng thái: {'MỞ' if self.state_manager.door_state == DoorState.UNLOCKED else 'KHOÁ'}"
        if self.use_freetype:
            text_surface, text_rect = self.font.render(status, (0, 0, 0))
            text_rect.topleft = (50, UI_CONFIG["APP_HEIGHT"] - 50)
            self.screen.blit(text_surface, text_rect)
        else:
            status_text = self.font.render(status, True, (0, 0, 0))
            self.screen.blit(status_text, (50, UI_CONFIG["APP_HEIGHT"] - 50))
        
        # Hiển thị trạng thái kết hợp để dễ hiểu
        door_lock_state = "ĐÃ KHÓA" if self.state_manager.door_state == DoorState.LOCKED else "ĐÃ MỞ KHÓA"
        door_physical_state = "ĐANG MỞ" if self.state_manager.door_physically_open else "ĐANG ĐÓNG"
        combined_status = f"Khóa: {door_lock_state} | Cánh cửa: {door_physical_state}"

        if self.use_freetype:
            text_surface, text_rect = self.font.render(combined_status, (0, 0, 100))
            text_rect.topleft = (50, UI_CONFIG["APP_HEIGHT"] - 80)
            self.screen.blit(text_surface, text_rect)
        else:
            status_text = self.font.render(combined_status, True, (0, 0, 100))
            self.screen.blit(status_text, (50, UI_CONFIG["APP_HEIGHT"] - 80))
        
        # Lấy logs từ log_service
        logs = self.log_service.get_recent_logs(5)
        
        # Vẽ nhật ký hoạt động gần đây
        if self.use_freetype:
            text_surface, text_rect = self.font.render("Nhật ký hoạt động gần đây:", (0, 0, 0))
            text_rect.topleft = (50, 420)
            self.screen.blit(text_surface, text_rect)
        else:
            log_title = self.font.render("Nhật ký hoạt động gần đây:", True, (0, 0, 0))
            self.screen.blit(log_title, (50, 420))
        
        for i, log in enumerate(reversed(logs)):
            log_text = f"{log['timestamp']} - {log['action']}"
            if self.use_freetype:
                text_surface, text_rect = self.font.render(log_text, (50, 50, 50))
                text_rect.topleft = (50, 450 + i * 20)
                self.screen.blit(text_surface, text_rect)
            else:
                log_render = self.font.render(log_text, True, (50, 50, 50))
                self.screen.blit(log_render, (50, 450 + i * 20))
        
        door_action = "ĐÓNG CÁNH CỬA" if self.state_manager.door_physically_open else "MỞ CÁNH CỬA"
        pygame.draw.rect(self.screen, (100, 100, 180), self.buttons["toggle_door"], border_radius=5)
        if self.use_freetype:
            text_surface, text_rect = self.font.render(door_action, (255, 255, 255))
            text_rect.center = self.buttons["toggle_door"].center
            self.screen.blit(text_surface, text_rect)
        else:
            text = self.font.render(door_action, True, (255, 255, 255))
            self.screen.blit(text, (self.buttons["toggle_door"].centerx - text.get_width() // 2, 
                                  self.buttons["toggle_door"].centery - text.get_height() // 2))
        
        # Cập nhật màn hình
        pygame.display.flip()
    
    def handle_events(self):
        """Xử lý các sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Xử lý nhập từ keypad
            key_pressed = self.keypad.handle_event(event)
            if key_pressed:
                continue
                
            # Xử lý click chuột
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Kiểm tra nút mở khoá
                if self.buttons["unlock"].collidepoint(mouse_pos):
                    # Thay vì mở khoá trực tiếp, hiển thị hộp thoại yêu cầu mật khẩu
                    self.show_password_dialog()
                
                # Kiểm tra nút khoá
                elif self.buttons["lock"].collidepoint(mouse_pos):
                    if self.state_manager.door_physically_open:
                        self.lcd.set_text("Không thể khóa", "Cửa đang mở!")
                        self.log_service.log_entry("Không thể khóa", "Cửa vẫn đang mở")
                        self.door_service.activate_buzzer(1)
                    else:
                        self.door_service.lock_door()
                        self.log_service.log_entry("Khóa cửa", "Khóa cửa từ giao diện GUI")
                
                elif self.buttons["toggle_door"].collidepoint(mouse_pos):
                    new_state = not self.state_manager.door_physically_open
                    self.state_manager.set_door_physical_state(new_state)
                    action = "Mở cánh cửa" if new_state else "Đóng cánh cửa"
                    self.log_service.log_entry(action, "Thay đổi từ giao diện")
        
        return True

    def show_password_dialog(self):
        """Hiển thị dialog yêu cầu nhập mật khẩu"""
        self.lcd.set_text("Nhập mã để", "mở khoá cửa")
        # Kích hoạt chế độ nhập mật khẩu (có thể thêm biến trạng thái để theo dõi)
        
    def run(self):
        """Chạy ứng dụng"""
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(UI_CONFIG["REFRESH_RATE"])
        
        # Dọn dẹp khi thoát
        pygame.quit()
        GPIO.cleanup()

# Chạy ứng dụng nếu đây là file chính
if __name__ == "__main__":
    app = DoorLockApp()
    app.run()
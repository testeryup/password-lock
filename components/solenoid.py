# components/solenoid.py
import pygame
from EmulatorGUI import GPIO

class SolenoidLock:
    def __init__(self, relay_pin, led_locked_pin, led_unlocked_pin, x=400, y=100, width=100, height=150):
        self.relay_pin = relay_pin
        self.led_locked_pin = led_locked_pin
        self.led_unlocked_pin = led_unlocked_pin
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Trạng thái khoá (mặc định là khoá)
        self.locked = True
    
    def lock(self):
        GPIO.output(self.relay_pin, GPIO.LOW)  # Tắt relay
        GPIO.output(self.led_locked_pin, GPIO.HIGH)  # Bật đèn đỏ
        GPIO.output(self.led_unlocked_pin, GPIO.LOW)  # Tắt đèn xanh
        self.locked = True
    
    def unlock(self):
        GPIO.output(self.relay_pin, GPIO.HIGH)  # Mở relay
        GPIO.output(self.led_locked_pin, GPIO.LOW)  # Tắt đèn đỏ
        GPIO.output(self.led_unlocked_pin, GPIO.HIGH)  # Bật đèn xanh
        self.locked = False
    
    def is_locked(self):
        return self.locked
    
    def draw(self, screen):
        # Vẽ khung khoá
        lock_color = (180, 0, 0) if self.locked else (0, 180, 0)
        pygame.draw.rect(screen, (80, 80, 80), 
                         (self.x, self.y, self.width, self.height))
        
        # Vẽ chốt khoá
        if self.locked:
            # Khoá đóng
            pygame.draw.rect(screen, lock_color, 
                            (self.x + self.width//4, self.y + self.height//4, 
                             self.width//2, self.height//2))
        else:
            # Khoá mở
            pygame.draw.rect(screen, lock_color, 
                            (self.x + self.width//4, self.y + self.height//4 + self.height//3,
                             self.width//2, self.height//6))
        
        # Vẽ đèn trạng thái
        # Đèn đỏ (khoá)
        red_status = (255, 0, 0) if self.locked else (100, 0, 0)
        pygame.draw.circle(screen, red_status, 
                          (self.x + self.width//4, self.y + self.height + 20), 10)
        
        # Đèn xanh (mở)
        green_status = (0, 255, 0) if not self.locked else (0, 100, 0)
        pygame.draw.circle(screen, green_status, 
                          (self.x + self.width - self.width//4, self.y + self.height + 20), 10)
# components/buzzer.py
import pygame
import threading
import time
from EmulatorGUI import GPIO

class Buzzer:
    def __init__(self, pin, x=400, y=300, radius=20):
        self.pin = pin
        self.x = x
        self.y = y
        self.radius = radius
        
        self.active = False
        self._buzz_thread = None
        # Thêm màu cảnh báo mặc định là vàng
        self.alert_color = (255, 255, 0)  # Màu vàng
        self.normal_color = (100, 100, 100)  # Màu xám khi không kích hoạt
        
    def start_buzz(self, duration=3.0):
        GPIO.output(self.pin, GPIO.HIGH)
        self.active = True  # Cập nhật trạng thái ở đây
        
        if self._buzz_thread:
            self._buzz_thread.cancel()
        
        self._buzz_thread = threading.Timer(duration, self.stop_buzz)
        self._buzz_thread.start()

    def stop_buzz(self):
        GPIO.output(self.pin, GPIO.LOW)
        self.active = False  # Cập nhật trạng thái ở đây
        
    def draw(self, screen):
        # Vẽ buzzer - không đọc từ GPIO mà sử dụng biến self.active đã có
        # self.active = GPIO.input(self.pin) == GPIO.HIGH  # Xóa dòng này
        
        # Chọn màu dựa trên trạng thái
        color = self.alert_color if self.active else self.normal_color
        
        # Vẽ buzzer
        pygame.draw.circle(screen, color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (50, 50, 50), (self.x, self.y), self.radius, 2)
        
        # Vẽ sóng âm khi kích hoạt
        if self.active:
            for i in range(1, 4):
                # Vẽ sóng với màu giống buzzer
                pygame.draw.circle(screen, self.alert_color, 
                                  (self.x, self.y), self.radius + i * 10, 1)
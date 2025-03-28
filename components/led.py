# components/led.py
import pygame
from EmulatorGUI import GPIO

class LED:
    def __init__(self, pin, x, y, color=(255, 0, 0), radius=10):
        self.pin = pin
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.off_color = (80, 80, 80)
        
        # Trạng thái đèn (mặc định là tắt)
        self.state = GPIO.LOW
    
    def set_state(self, state):
        self.state = state
        GPIO.output(self.pin, state)
    
    def toggle(self):
        if self.state == GPIO.LOW:
            self.set_state(GPIO.HIGH)
        else:
            self.set_state(GPIO.LOW)
    
    def is_on(self):
        return self.state == GPIO.HIGH
    
    def draw(self, screen):
        # Vẽ đèn LED
        if self.state == GPIO.HIGH:
            led_color = self.color
            # Hiệu ứng sáng xung quanh
            pygame.draw.circle(screen, (self.color[0], self.color[1], self.color[2], 50), 
                             (self.x, self.y), self.radius + 5)
        else:
            led_color = self.off_color
        
        pygame.draw.circle(screen, led_color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (20, 20, 20), (self.x, self.y), self.radius, 1)
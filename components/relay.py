# components/relay.py
import pygame
from EmulatorGUI import GPIO

class Relay:
    def __init__(self, pin, x=400, y=200, width=60, height=40):
        self.pin = pin
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Trạng thái relay (mặc định là tắt)
        self.state = GPIO.LOW
    
    def set_state(self, state):
        self.state = state
        GPIO.output(self.pin, state)
    
    def toggle(self):
        if self.state == GPIO.LOW:
            self.set_state(GPIO.HIGH)
        else:
            self.set_state(GPIO.LOW)
    
    def is_active(self):
        return self.state == GPIO.HIGH
    
    def draw(self, screen):
        # Vẽ relay
        relay_color = (0, 150, 0) if self.state == GPIO.HIGH else (150, 0, 0)
        
        # Vẽ thân relay
        pygame.draw.rect(screen, (100, 100, 100), 
                       (self.x, self.y, self.width, self.height))
        
        # Vẽ trạng thái kích hoạt
        pygame.draw.rect(screen, relay_color, 
                       (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        
        # Vẽ chữ
        font = pygame.font.SysFont('Arial', 12)
        text = "ON" if self.state == GPIO.HIGH else "OFF"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        screen.blit(text_surface, text_rect)
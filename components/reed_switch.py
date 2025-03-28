# components/reed_switch.py
import pygame

class ReedSwitch:
    def __init__(self, pin, x=550, y=150, width=100, height=80):
        self.pin = pin
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Trạng thái cửa (mặc định là đóng)
        self.door_open = False
        
    def set_door_open(self, is_open):
        self.door_open = is_open
        
    def is_door_open(self):
        return self.door_open
    
    def draw(self, screen):
        # Vẽ khung cảm biến
        pygame.draw.rect(screen, (200, 200, 200), 
                         (self.x, self.y, self.width, self.height))
        
        # Làm rõ ràng hơn về trạng thái
        status_text = "CÁNH CỬA: MỞ" if self.door_open else "CÁNH CỬA: ĐÓNG"
        status_color = (255, 0, 0) if self.door_open else (0, 180, 0)  # Đỏ khi mở, xanh khi đóng
        
        try:
            font = pygame.freetype.Font("fonts/Roboto-Regular.ttf", 16)
            text_surface, text_rect = font.render(status_text, status_color)
            text_rect.center = (self.x + self.width//2, self.y + self.height//2)
            screen.blit(text_surface, text_rect)
        except:
            font = pygame.font.SysFont('Arial', 16)
            text = font.render(status_text, True, status_color)
            text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            screen.blit(text, text_rect)
        
        # Vẽ cửa
        door_x = self.x + self.width + 10
        door_color = (150, 75, 0)
        
        if not self.door_open:
            # Cửa đóng
            pygame.draw.rect(screen, door_color, (door_x, self.y - 20, 15, self.height + 40))
        else:
            # Cửa mở
            pygame.draw.polygon(screen, door_color, [
                (door_x, self.y - 20),
                (door_x + 50, self.y),
                (door_x + 50, self.y + self.height),
                (door_x, self.y + self.height + 20)
            ])
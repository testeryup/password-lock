# components/lcd.py
import pygame

class LCD:
    def __init__(self, x=50, y=50, width=300, height=80):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.text = ["SmartLock", "Nhập mã..."]
        self.backlight_color = (64, 128, 128)
        self.text_color = (0, 0, 0)
        
        # Tải font hỗ trợ tiếng Việt
        try:
            self.font = pygame.freetype.Font("fonts/Roboto-Regular.ttf", 16)
            self.use_freetype = True
        except:
            self.font = pygame.font.SysFont('Courier New', 16)
            self.use_freetype = False
    
    def set_text(self, line1, line2=""):
        if isinstance(line1, list):
            self.text = line1[:2]
        else:
            self.text = [str(line1), str(line2)]
    
    def set_backlight(self, r, g, b):
        self.backlight_color = (r, g, b)
    
    def draw(self, screen):
        # Vẽ viền LCD
        pygame.draw.rect(screen, (50, 50, 50), 
                         (self.x - 5, self.y - 5, self.width + 10, self.height + 10))
        
        # Vẽ nền LCD
        pygame.draw.rect(screen, self.backlight_color, 
                         (self.x, self.y, self.width, self.height))
        
        # Vẽ text
        for i, line in enumerate(self.text[:2]):  # Tối đa 2 dòng
            # Giới hạn độ dài dòng (16 ký tự cho LCD 16x2)
            if len(line) > 16:
                line = line[:16]
                
            if self.use_freetype:
                text_surface, text_rect = self.font.render(line, self.text_color)
                screen.blit(text_surface, (self.x + 10, self.y + 10 + (i * 30)))
            else:
                text_surface = pygame.font.SysFont('Courier New', 16).render(line, True, self.text_color)
                screen.blit(text_surface, (self.x + 10, self.y + 10 + (i * 30)))
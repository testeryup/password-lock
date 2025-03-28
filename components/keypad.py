# components/keypad.py
import pygame

class Keypad:
    def __init__(self, x=50, y=150, width=200, height=250):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.keys = [
            '1', '2', '3', 'A',
            '4', '5', '6', 'B',
            '7', '8', '9', 'C',
            '*', '0', '#', 'D'
        ]
        
        self.key_width = self.width // 4
        self.key_height = self.height // 4
        
        self.callback = None
        self.current_input = ""
        self.max_length = 4
        
    def set_callback(self, callback):
        self.callback = callback
    
    def draw(self, screen):
        # Vẽ nền keypad
        pygame.draw.rect(screen, (200, 200, 200), 
                         (self.x - 10, self.y - 10, 
                          self.width + 20, self.height + 20))
        
        # Vẽ từng phím
        for i, key in enumerate(self.keys):
            row = i // 4
            col = i % 4
            
            key_x = self.x + col * self.key_width
            key_y = self.y + row * self.key_height
            
            color = (150, 150, 150)
            if key in ['A', 'B', 'C', 'D']:
                color = (100, 100, 180)
            elif key in ['*', '#']:
                color = (180, 100, 100)
            
            # Vẽ phím
            pygame.draw.rect(screen, color, 
                            (key_x, key_y, self.key_width - 5, self.key_height - 5),
                            0, 3)
            
            # Viền phím
            pygame.draw.rect(screen, (50, 50, 50), 
                            (key_x, key_y, self.key_width - 5, self.key_height - 5),
                            1, 3)
            
            # Chữ trên phím
            font = pygame.font.SysFont('Arial', 24)
            text = font.render(key, True, (0, 0, 0))
            text_rect = text.get_rect(center=(key_x + self.key_width//2, key_y + self.key_height//2))
            screen.blit(text, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            
            if (self.x <= pos[0] <= self.x + self.width and 
                self.y <= pos[1] <= self.y + self.height):
                
                col = (pos[0] - self.x) // self.key_width
                row = (pos[1] - self.y) // self.key_height
                
                if 0 <= row < 4 and 0 <= col < 4:
                    key_index = row * 4 + col
                    key_pressed = self.keys[key_index]
                    
                    self.process_key(key_pressed)
                    return key_pressed
        
        return None
    
    def process_key(self, key):
        if key in "0123456789" and len(self.current_input) < self.max_length:
            self.current_input += key
        elif key == "C":  # Clear
            self.current_input = ""
        elif key == "D":  # Enter/Submit
            if self.callback and self.current_input:
                self.callback(self.current_input)
                self.current_input = ""
import pygame

class Player:
    def __init__(self, screen_width, screen_height, ship_type="default"):
        self.width = 100
        self.height = 100

        self.speed = 5

        # Load the correct ship image based on the selection
        try:
            if ship_type == "advanced":
                path = "assets/images/ship2.png"
            else:
                path = "assets/images/ship1.png"
            
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except Exception as e:
            print(f"Ship image not found: {e}")
            self.image = None

        self.x = screen_width // 2 - self.width // 2
        self.y = screen_height - 100

        self.screen_width = screen_width 

        self.is_blinking = False
        self.blink_timer = 0
        self.visible = True
    
    def move_left(self):
        if not self.is_blinking:
            self.x -= self.speed

    def move_right(self):
        if not self.is_blinking:
            self.x += self.speed

    def keep_inside_screen(self):
        self.x = max(0, min(self.x, self.screen_width - self.width))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_blink(self):
        if self.is_blinking:
            self.blink_timer += 1
            # Alternate visibility every 10 frames
            if self.blink_timer % 10 == 0:
                self.visible = not self.visible
        else:
            self.visible = True

    def draw(self, screen):
        if self.visible:
            if self.image:
                screen.blit(self.image, (self.x, self.y))
            else:
                pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))
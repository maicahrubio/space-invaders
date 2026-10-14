import pygame

class Enemy:
    def __init__(self, index, total_enemies, screen_width, is_boss=False):
        self.is_boss = is_boss
        self.screen_width = screen_width
        
        if self.is_boss:
            self.width = 150
            self.height = 150
            try:
                self.image = pygame.image.load("assets/images/bigboss.png").convert_alpha()
            except pygame.error:
                self.image = pygame.image.load("assets/images/enemy2.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.health = 5  # Takes 5 hits to defeat!
            self.boss_dir = 1  # 1 for right, -1 for left
            self.shoot_timer = 0
        else:
            self.width = 80
            self.height = 80
            self.image = pygame.image.load("assets/images/enemy2.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            self.health = 1

        spacing = screen_width / (total_enemies + 1)
        self.target_mid_x = spacing * (index + 1) - (self.width // 2)
        
        if self.is_boss:
            self.target_mid_x = screen_width // 2 - self.width // 2
            self.target_mid_y = 100
        else:
            self.target_mid_y = 150 + (50 if index % 2 == 0 else 0)

        self.x = self.target_mid_x
        self.y = -150 if self.is_boss else -100

        self.state = "entering" 
        self.speed = 4
        self.dx = 0
        self.dy = 0

    def start_drop(self, target_x, target_y):
        if self.is_boss:
            return  # Boss doesn't drop down like regular enemies
        self.state = "dropping"
        
        distance_x = target_x - self.x
        distance_y = target_y - self.y
        distance = (distance_x**2 + distance_y**2)**0.5

        if distance > 0:
            self.dx = (distance_x / distance) * self.speed
            self.dy = (distance_y / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed

    def update(self):
        if self.state == "entering":
            if self.y < self.target_mid_y:
                self.y += 2
            else:
                self.y = self.target_mid_y
                self.state = "waiting"

        elif self.state == "waiting" and self.is_boss:
            # Move left and right across the top of the screen
            self.x += 3 * self.boss_dir
            if self.x <= 50 or self.x >= self.screen_width - self.width - 50:
                self.boss_dir *= -1  # Reverse direction

        elif self.state == "dropping":
            self.x += self.dx
            self.y += self.dy
            
            if self.y > 650 or self.x < -150 or self.x > 950:
                self.state = "offscreen"

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.state != "offscreen":
            screen.blit(self.image, (self.x, self.y))
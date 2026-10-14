import pygame
import random
from entities.player import Player
from entities.button import MobileButtons
from entities.enemy import Enemy
from entities.bullet import Bullet
from settings import load_settings, save_settings
from database import (
    register_player_and_score, 
    get_leaderboard, 
    register_user, 
    verify_user, 
    update_player_username, 
    update_player_ship
)

class GameManager:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.settings = load_settings()

        # Arcade Fonts
        self.font = pygame.font.SysFont("Courier New", 28, bold=True)
        self.big_font = pygame.font.SysFont("Courier New", 48, bold=True)
        self.small_font = pygame.font.SysFont("Courier New", 20, bold=True)
        
        # Load the custom logo image safely from assets/images/
        try:
            raw_logo = pygame.image.load("assets/images/logo.png").convert_alpha()
            self.logo_image = pygame.transform.scale(raw_logo, (460, 160))
        except Exception as e:
            print(f"Logo image not found: {e}")
            self.logo_image = None

        # Load Ship Preview Images safely from assets/images/
        try:
            self.ship1_img = pygame.transform.scale(pygame.image.load("assets/images/ship1.png").convert_alpha(), (64, 64))
        except:
            self.ship1_img = None

        try:
            self.ship2_img = pygame.transform.scale(pygame.image.load("assets/images/ship2.png").convert_alpha(), (64, 64))
        except:
            self.ship2_img = None

        # Game States
        self.game_state = "login"
        
        # User session variables
        self.username = ""
        self.password = ""
        self.logged_in_user = None
        self.selected_ship = "default"
        self.feedback_message = ""
        self.active_input = "username"
        self.home_editing = False  # For editing name on home screen
        
        # Moving Starfield Background setup
        self.stars = [[random.randint(0, screen_width), random.randint(0, screen_height), random.uniform(0.5, 2.0)] for _ in range(80)]
        
        # UI Layout - Login Screen
        self.login_user_box = pygame.Rect(screen_width // 2 - 160, screen_height // 2 - 25, 320, 45)
        self.login_pass_box = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 50, 320, 45)
        self.login_button_rect = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 115, 320, 45)
        self.to_register_button_rect = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 170, 320, 40)
        
        # UI Layout - Register Screen
        self.reg_user_box = pygame.Rect(screen_width // 2 - 160, screen_height // 2 - 25, 320, 45)
        self.reg_pass_box = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 50, 320, 45)
        self.reg_button_rect = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 115, 320, 45)
        self.back_to_login_rect = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 170, 320, 40)

       # UI Layout - Home Page (Centered & Quit moved to bottom right)
        start_y = screen_height // 2 - 100
        self.home_edit_name_box = pygame.Rect(screen_width // 2 - 160, start_y, 320, 40)
        self.home_save_name_rect = pygame.Rect(screen_width // 2 - 160, start_y + 48, 320, 35)
        self.home_ship_rect = pygame.Rect(screen_width // 2 - 160, start_y + 91, 320, 45)
        self.home_play_rect = pygame.Rect(screen_width // 2 - 160, start_y + 144, 320, 50)
        self.home_lb_rect = pygame.Rect(screen_width // 2 - 160, start_y + 202, 320, 40)
        self.home_settings_rect = pygame.Rect(screen_width // 2 - 160, start_y + 254, 320, 40)

        # Quit button moved to the bottom right corner
        self.home_logout_rect = pygame.Rect(screen_width - 150, screen_height - 60, 130, 40)
        # UI Layout - Ship Selection
        self.ship1_rect = pygame.Rect(screen_width // 2 - 220, screen_height // 2 - 60, 180, 130)
        self.ship2_rect = pygame.Rect(screen_width // 2 + 40, screen_height // 2 - 60, 180, 130)
        self.ship_back_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 100, 200, 45)

        # UI Layout - Settings Screen
        self.settings_toggle_controls_rect = pygame.Rect(screen_width // 2 - 160, screen_height // 2 - 60, 320, 45)
        self.settings_toggle_music_rect = pygame.Rect(screen_width // 2 - 160, screen_height // 2 + 5, 320, 45)
        self.settings_back_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 80, 200, 40)

        # In-game generic buttons
        self.reload_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 10, 200, 40)
        self.leaderboard_button_rect = pygame.Rect(screen_width // 2 - 125, screen_height // 2 + 65, 250, 45)
        self.back_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height - 80, 200, 45)
        
        self.reset_game_variables()

    # In-game generic buttons
        self.reload_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 10, 200, 40)
        self.leaderboard_button_rect = pygame.Rect(screen_width // 2 - 125, screen_height // 2 + 65, 250, 45)
        self.back_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height - 80, 200, 45)
        
        self.reset_game_variables()

    def reset_game_variables(self):
        self.level = 1  # <-- Add this line right here!
        self.player = Player(self.screen_width, self.screen_height, self.selected_ship)
        self.buttons = MobileButtons()
        self.bullet = None
        self.enemies = []
        self.score = 0
        self.spawn_number = 5
        self.score_saved = False  
        self.player_history = [] 
        self.timer = 0
        self.state_timer = 0
        self.spawn_enemies()

    def spawn_enemies(self):
        self.enemies = []
        
        # LEVEL 5, 10, 15, 20...: THE BIG BOSS ENCOUNTER!
        if self.level > 0 and self.level % 5 == 0:
            boss = Enemy(0, 1, self.screen_width, is_boss=True) 
            boss.image = pygame.image.load("assets/images/bigboss.png").convert_alpha()
            boss.image = pygame.transform.scale(boss.image, (100, 100))
            boss.rect = boss.image.get_rect(topleft=(self.screen_width // 2 - 50, 100))
            self.enemies.append(boss)
            self.timer = 0
            return

        # REGULAR LEVELS: Use different enemy images based on level and mix them up
        for i in range(self.spawn_number):
            enemy = Enemy(i, self.spawn_number, self.screen_width)
            
            # Mix up colors for variety across levels
            if self.level == 1:
                img_path = "assets/images/enemy2.png"
            elif self.level in [2, 3]:
                img_path = "assets/images/enemy3.png" if i % 2 == 0 else "assets/images/enemy2.png"
            else:
                img_path = "assets/images/enemy4.png" if i % 2 == 0 else "assets/images/enemy3.png"
                
            enemy.image = pygame.image.load(img_path).convert_alpha()
            enemy.image = pygame.transform.scale(enemy.image, (50, 50))
            enemy.rect = enemy.image.get_rect(topleft=(enemy.x, enemy.y))
            
            self.enemies.append(enemy)
            
        self.timer = 0

    def update_starfield(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > self.screen_height:
                star[1] = 0
                star[0] = random.randint(0, self.screen_width)

    def update(self, events):
        self.update_starfield()

        # Check if all enemies are defeated -> Level Up!
        if len(self.enemies) == 0 and self.game_state == "playing":
            self.level += 1
            print("CURRENT LEVEL IS NOW:", self.level)  # Temporary check
            
            if self.level == 6:
                self.spawn_number = 9
            elif self.level != 5:
                self.spawn_number += 1
            self.spawn_enemies()

        # 1. LOGIN SCREEN STATE
        if self.game_state == "login":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.active_input = "password" if self.active_input == "username" else "username"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.active_input == "username":
                            self.username = self.username[:-1]
                        else:
                            self.password = self.password[:-1]
                    elif event.key == pygame.K_RETURN:
                        success, result = verify_user(self.username, self.password)
                        if success:
                            self.logged_in_user = result['username']
                            self.selected_ship = result.get('selected_ship', 'default')
                            self.feedback_message = ""
                            self.game_state = "home"
                            
                            # Start background music on successful login (Enter Key)
                            pygame.mixer.music.load("assets/sounds/bg.mp3")
                            pygame.mixer.music.play(-1)
                        else:
                            self.feedback_message = result
                    else:
                        if self.active_input == "username" and len(self.username) < 15:
                            self.username += event.unicode
                        elif self.active_input == "password" and len(self.password) < 15:
                            self.password += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.login_user_box.collidepoint(event.pos):
                        self.active_input = "username"
                    elif self.login_pass_box.collidepoint(event.pos):
                        self.active_input = "password"
                    elif self.login_button_rect.collidepoint(event.pos):
                        success, result = verify_user(self.username, self.password)
                        if success:
                            self.logged_in_user = result['username']
                            self.selected_ship = result.get('selected_ship', 'default')
                            self.feedback_message = ""
                            self.game_state = "home"
                            
                            # Start background music on successful login (Mouse Click)
                            pygame.mixer.music.load("assets/sounds/bg.mp3")
                            pygame.mixer.music.play(-1)
                        else:
                            self.feedback_message = result
                    elif self.to_register_button_rect.collidepoint(event.pos):
                        self.username = ""
                        self.password = ""
                        self.feedback_message = ""
                        self.game_state = "register"

        # 2. REGISTER SCREEN STATE
        elif self.game_state == "register":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.active_input = "password" if self.active_input == "username" else "username"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.active_input == "username":
                            self.username = self.username[:-1]
                        else:
                            self.password = self.password[:-1]
                    elif event.key == pygame.K_RETURN:
                        success, msg = register_user(self.username, self.password)
                        self.feedback_message = msg
                        if success:
                            self.game_state = "login"
                    else:
                        if self.active_input == "username" and len(self.username) < 15:
                            self.username += event.unicode
                        elif self.active_input == "password" and len(self.password) < 15:
                            self.password += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.reg_user_box.collidepoint(event.pos):
                        self.active_input = "username"
                    elif self.reg_pass_box.collidepoint(event.pos):
                        self.active_input = "password"
                    elif self.reg_button_rect.collidepoint(event.pos):
                        success, msg = register_user(self.username, self.password)
                        self.feedback_message = msg
                        if success:
                            self.game_state = "login"
                    elif self.back_to_login_rect.collidepoint(event.pos):
                        self.username = ""
                        self.password = ""
                        self.feedback_message = ""
                        self.game_state = "login"

        # 3. HOME PAGE STATE
        elif self.game_state == "home":
            for event in events:
                if event.type == pygame.KEYDOWN and self.home_editing:
                    if event.key == pygame.K_BACKSPACE:
                        self.logged_in_user = self.logged_in_user[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.logged_in_user.strip() != "":
                            update_player_username(self.username, self.logged_in_user)
                            self.username = self.logged_in_user
                            self.feedback_message = "Name saved!"
                            self.home_editing = False
                    else:
                        if len(self.logged_in_user) < 15:
                            self.logged_in_user += event.unicode

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.home_edit_name_box.collidepoint(event.pos):
                        self.home_editing = True
                        self.feedback_message = ""
                    else:
                        self.home_editing = False

                    if self.home_save_name_rect.collidepoint(event.pos):
                        if self.logged_in_user.strip() != "":
                            update_player_username(self.username, self.logged_in_user)
                            self.username = self.logged_in_user
                            self.feedback_message = "Name saved!"
                            self.home_editing = False
                    elif self.home_ship_rect.collidepoint(event.pos):
                        self.game_state = "ship_select"
                    elif self.home_play_rect.collidepoint(event.pos):
                        self.username = self.logged_in_user
                        self.game_state = "playing"
                        self.reset_game_variables()
                    elif self.home_lb_rect.collidepoint(event.pos):
                        self.game_state = "leaderboard"
                    elif self.home_settings_rect.collidepoint(event.pos):
                        self.game_state = "settings"
                    elif self.home_logout_rect.collidepoint(event.pos):
                        self.username = ""
                        self.password = ""
                        self.logged_in_user = None
                        self.home_editing = False
                        self.game_state = "login"
                        
                        # STOP MUSIC WHEN LOGGING OUT / RETURNING TO LOGIN SCREEN
                        pygame.mixer.music.stop()

        # --- SETTINGS SCREEN STATE ---
        elif self.game_state == "settings":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.settings_back_rect.collidepoint(event.pos):
                        self.game_state = "home"
                    elif self.settings_toggle_controls_rect.collidepoint(event.pos):
                        current_val = self.settings.get("mobile_controls", False)
                        self.settings["mobile_controls"] = not bool(current_val)
                        save_settings(self.settings)
                    elif self.settings_toggle_music_rect.collidepoint(event.pos):
                        if self.settings.get("sound_volume", 80) > 0:
                            self.settings["sound_volume"] = 0
                            pygame.mixer.music.pause()
                        else:
                            self.settings["sound_volume"] = 80
                            pygame.mixer.music.unpause()
                        save_settings(self.settings)

        # 4. SHIP SELECT STATE
        elif self.game_state == "ship_select":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.ship1_rect.collidepoint(event.pos):
                        self.selected_ship = "default"
                        update_player_ship(self.logged_in_user, self.selected_ship)
                        self.game_state = "home"
                    elif self.ship2_rect.collidepoint(event.pos):
                        self.selected_ship = "advanced"
                        update_player_ship(self.logged_in_user, self.selected_ship)
                        self.game_state = "home"
                    elif self.ship_back_rect.collidepoint(event.pos):
                        self.game_state = "home"

        # 5. PLAYING / BLINKING STATES
        elif self.game_state == "playing" or self.game_state == "blinking":
            self.player_history.append((self.player.x, self.player.y))
            if len(self.player_history) > 60:
                self.player_history.pop(0)

            if self.game_state == "playing":
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.player.move_left()
                if keys[pygame.K_RIGHT]:
                    self.player.move_right()

                screen_button_fired = self.buttons.handle_mouse(self.player, events)
                
                keyboard_fired = False
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        keyboard_fired = True

                    # Check if player clicks the Pause button "II"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if hasattr(self, 'pause_button_rect') and self.pause_button_rect.collidepoint(event.pos):
                            self.game_state = "paused"

                if (screen_button_fired or keyboard_fired) and self.bullet is None:
                    self.bullet = Bullet(self.player.x + self.player.width // 2 - 16, self.player.y)

                self.player.keep_inside_screen()

                if self.bullet:
                    self.bullet.update()
                    if not self.bullet.is_active:
                        self.bullet = None

                self.timer += 1
                if self.timer >= 180:
                    waiting_enemies = [e for e in self.enemies if e.state == "waiting"]
                    if waiting_enemies:
                        chosen_enemy = random.choice(waiting_enemies)
                        target_x, target_y = self.player_history[0]
                        chosen_enemy.start_drop(target_x, target_y)
                    self.timer = 0

                all_despawned = True
                for enemy in self.enemies:
                    enemy.update()
                    if enemy.state != "offscreen":
                        all_despawned = False


                self.check_collisions()

                if all_despawned:
                    self.level += 1
                    print("CURRENT LEVEL IS NOW:", self.level)
        
                    if self.level == 6:
                        self.spawn_number = 9
                    elif self.level != 5:
                        self.spawn_number += 1
                    self.spawn_enemies()

            elif self.game_state == "blinking":
                self.player.update_blink()
                self.state_timer += 1
                for enemy in self.enemies:
                    enemy.update()

                if self.state_timer >= 180: 
                    self.game_state = "game_over"

        elif self.game_state == "paused":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'resume_button_rect') and self.resume_button_rect.collidepoint(event.pos):
                        self.game_state = "playing"
                    elif hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(event.pos):
                        self.score = 0
                        self.level = 1
                        self.game_state = "playing"
                        self.spawn_enemies()
                    elif hasattr(self, 'home_button_rect') and self.home_button_rect.collidepoint(event.pos):
                        self.game_state = "home"

        # 6. GAME OVER STATE
        elif self.game_state == "game_over":
            if not self.score_saved:
                register_player_and_score(self.logged_in_user if self.logged_in_user else "Guest", self.score)
                self.score_saved = True

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.reload_button_rect.collidepoint(event.pos):
                        self.reset_game_variables()
                        self.game_state = "playing"
                    elif self.leaderboard_button_rect.collidepoint(event.pos):
                        self.game_state = "leaderboard"

        # 7. LEADERBOARD STATE
        elif self.game_state == "leaderboard":
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_button_rect.collidepoint(event.pos):
                        self.game_state = "home" if self.logged_in_user else "game_over"
                        
        # ================= RENDERING SECTION =================
        if self.game_state in ["login", "register"]:
            self.screen.fill((15, 22, 45))
        else:
            self.screen.fill((0, 0, 0))
            for star in self.stars:
                pygame.draw.circle(self.screen, (255, 255, 255), (int(star[0]), int(star[1])), 1)
        
        # --- LOGIN SCREEN ---
        if self.game_state == "login":
            if self.logo_image:
                self.screen.blit(self.logo_image, (self.screen_width // 2 - self.logo_image.get_width() // 2, 40))
            else:
                title_text = self.big_font.render("SPACE INVADERS", True, (255, 255, 0))
                self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 60))

            user_label = self.small_font.render("USERNAME:", True, (180, 200, 255))
            self.screen.blit(user_label, (self.login_user_box.x, self.login_user_box.y - 24))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "username" else (80, 100, 140), self.login_user_box, 2)
            u_surf = self.font.render(self.username, True, (255, 255, 255))
            self.screen.blit(u_surf, (self.login_user_box.x + 10, self.login_user_box.y + 6))

            pass_label = self.small_font.render("PASSWORD:", True, (180, 200, 255))
            self.screen.blit(pass_label, (self.login_pass_box.x, self.login_pass_box.y - 24))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "password" else (80, 100, 140), self.login_pass_box, 2)
            p_surf = self.font.render("*" * len(self.password), True, (255, 255, 255))
            self.screen.blit(p_surf, (self.login_pass_box.x + 10, self.login_pass_box.y + 6))

            if self.feedback_message:
                fb_surf = self.small_font.render(self.feedback_message, True, (255, 90, 90))
                self.screen.blit(fb_surf, (self.screen_width // 2 - fb_surf.get_width() // 2, self.login_pass_box.y + 50))

            pygame.draw.rect(self.screen, (0, 180, 80), self.login_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 255, 150), self.login_button_rect, 2, border_radius=4)
            l_text = self.font.render("LOGIN", True, (255, 255, 255))
            self.screen.blit(l_text, (self.login_button_rect.x + (self.login_button_rect.width // 2 - l_text.get_width() // 2),
                                      self.login_button_rect.y + (self.login_button_rect.height // 2 - l_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (30, 90, 180), self.to_register_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 180, 255), self.to_register_button_rect, 2, border_radius=4)
            r_text = self.small_font.render("CREATE ACCOUNT", True, (255, 255, 255))
            self.screen.blit(r_text, (self.to_register_button_rect.x + (self.to_register_button_rect.width // 2 - r_text.get_width() // 2),
                                      self.to_register_button_rect.y + (self.to_register_button_rect.height // 2 - r_text.get_height() // 2)))
        # --- SETTINGS SCREEN DRAWING ---
        elif self.game_state == "settings":
            self.screen.fill((10, 15, 30))  # Dark space background
            
            # Title
            title_text = self.big_font.render("SETTINGS", True, (255, 255, 255))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))
            
            # Toggle Controls Button Text & Drawing
            pygame.draw.rect(self.screen, (25, 45, 85), self.settings_toggle_controls_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.settings_toggle_controls_rect, 2, border_radius=16)
            controls_status = "ON" if bool(self.settings.get("mobile_controls", False)) else "OFF"
            controls_text = self.small_font.render(f"Mobile Controls: {controls_status}", True, (220, 240, 255))
            self.screen.blit(controls_text, (self.settings_toggle_controls_rect.x + (self.settings_toggle_controls_rect.width // 2 - controls_text.get_width() // 2),
                                             self.settings_toggle_controls_rect.y + (self.settings_toggle_controls_rect.height // 2 - controls_text.get_height() // 2)))
            
            # Toggle Music Button Text & Drawing
            pygame.draw.rect(self.screen, (25, 45, 85), self.settings_toggle_music_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.settings_toggle_music_rect, 2, border_radius=16)
            music_status = "ON" if self.settings.get("sound_volume", 80) > 0 else "OFF"
            music_text = self.small_font.render(f"Background Music: {music_status}", True, (220, 240, 255))
            self.screen.blit(music_text, (self.settings_toggle_music_rect.x + (self.settings_toggle_music_rect.width // 2 - music_text.get_width() // 2),
                                          self.settings_toggle_music_rect.y + (self.settings_toggle_music_rect.height // 2 - music_text.get_height() // 2)))
            
            # Back Button
            pygame.draw.rect(self.screen, (25, 45, 85), self.settings_back_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.settings_back_rect, 2, border_radius=16)
            back_text = self.small_font.render("Back", True, (220, 240, 255))
            self.screen.blit(back_text, (self.settings_back_rect.x + (self.settings_back_rect.width // 2 - back_text.get_width() // 2),
                                         self.settings_back_rect.y + (self.settings_back_rect.height // 2 - back_text.get_height() // 2)))

        # --- REGISTER SCREEN ---
        elif self.game_state == "register":
            if self.logo_image:
                self.screen.blit(self.logo_image, (self.screen_width // 2 - self.logo_image.get_width() // 2, 40))
            else:
                title_text = self.big_font.render("REGISTER", True, (255, 255, 0))
                self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 60))

            user_label = self.small_font.render("CHOOSE USERNAME:", True, (180, 200, 255))
            self.screen.blit(user_label, (self.reg_user_box.x, self.reg_user_box.y - 24))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "username" else (80, 100, 140), self.reg_user_box, 2)
            u_surf = self.font.render(self.username, True, (255, 255, 255))
            self.screen.blit(u_surf, (self.reg_user_box.x + 10, self.reg_user_box.y + 6))

            pass_label = self.small_font.render("CHOOSE PASSWORD:", True, (180, 200, 255))
            self.screen.blit(pass_label, (self.reg_pass_box.x, self.reg_pass_box.y - 24))
            pygame.draw.rect(self.screen, (0, 255, 200) if self.active_input == "password" else (80, 100, 140), self.reg_pass_box, 2)
            p_surf = self.font.render("*" * len(self.password), True, (255, 255, 255))
            self.screen.blit(p_surf, (self.reg_pass_box.x + 10, self.reg_pass_box.y + 6))

            if self.feedback_message:
                fb_surf = self.small_font.render(self.feedback_message, True, (255, 90, 90))
                self.screen.blit(fb_surf, (self.screen_width // 2 - fb_surf.get_width() // 2, self.reg_pass_box.y + 50))

            pygame.draw.rect(self.screen, (0, 180, 80), self.reg_button_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 255, 150), self.reg_button_rect, 2, border_radius=4)
            reg_text = self.font.render("SIGN UP", True, (255, 255, 255))
            self.screen.blit(reg_text, (self.reg_button_rect.x + (self.reg_button_rect.width // 2 - reg_text.get_width() // 2),
                                        self.reg_button_rect.y + (self.reg_button_rect.height // 2 - reg_text.get_height() // 2)))

            pygame.draw.rect(self.screen, (160, 40, 40), self.back_to_login_rect, border_radius=4)
            pygame.draw.rect(self.screen, (255, 100, 100), self.back_to_login_rect, 2, border_radius=4)
            back_t = self.small_font.render("BACK TO LOGIN", True, (255, 255, 255))
            self.screen.blit(back_t, (self.back_to_login_rect.x + (self.back_to_login_rect.width // 2 - back_t.get_width() // 2),
                                      self.back_to_login_rect.y + (self.back_to_login_rect.height // 2 - back_t.get_height() // 2)))

        # --- HOME PAGE ---
        elif self.game_state == "home":
            main_title = self.big_font.render("SPACE INVADERS", True, (120, 180, 255))
            self.screen.blit(main_title, (self.screen_width // 2 - main_title.get_width() // 2, 40))
            
            sub_title = self.font.render("REVENGE OF THE GALAXY", True, (240, 220, 80))
            self.screen.blit(sub_title, (self.screen_width // 2 - sub_title.get_width() // 2, 90))
            prompt_label = self.small_font.render("PILOT CALLSIGN:", True, (180, 200, 255))
            self.screen.blit(prompt_label, (self.home_edit_name_box.x, self.home_edit_name_box.y - 22))
            
            box_border_color = (0, 255, 100) if self.home_editing else (0, 255, 200)
            pygame.draw.rect(self.screen, box_border_color, self.home_edit_name_box, 2)
            name_surf = self.font.render(self.logged_in_user, True, (255, 255, 255))
            self.screen.blit(name_surf, (self.home_edit_name_box.x + 10, self.home_edit_name_box.y + 4))

            if self.feedback_message:
                fb = self.small_font.render(self.feedback_message, True, (80, 255, 150))
                self.screen.blit(fb, (self.screen_width // 2 - fb.get_width() // 2, self.home_edit_name_box.y - 50))

            # Save Name Button (Arcade Pill Style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.home_save_name_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.home_save_name_rect, 2, border_radius=16)
            sn_text = self.small_font.render("Update Name", True, (220, 240, 255))
            self.screen.blit(sn_text, (self.home_save_name_rect.x + (self.home_save_name_rect.width // 2 - sn_text.get_width() // 2),
                                       self.home_save_name_rect.y + (self.home_save_name_rect.height // 2 - sn_text.get_height() // 2)))

            # Pick Ship Button (Arcade Pill Style) -> Options style
            pygame.draw.rect(self.screen, (25, 45, 85), self.home_ship_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.home_ship_rect, 2, border_radius=16)
            ship_text = self.small_font.render("Ship Style", True, (220, 240, 255))
            self.screen.blit(ship_text, (self.home_ship_rect.x + (self.home_ship_rect.width // 2 - ship_text.get_width() // 2),
                                         self.home_ship_rect.y + (self.home_ship_rect.height // 2 - ship_text.get_height() // 2)))
            # Play Button (Arcade Pill Style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.home_play_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.home_play_rect, 2, border_radius=16)
            play_text = self.small_font.render("Save the World", True, (220, 240, 255))
            self.screen.blit(play_text, (self.home_play_rect.x + (self.home_play_rect.width // 2 - play_text.get_width() // 2),
                                         self.home_play_rect.y + (self.home_play_rect.height // 2 - play_text.get_height() // 2)))
            # Leaderboard Button (Arcade Pill Style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.home_lb_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.home_lb_rect, 2, border_radius=16)
            lb_text = self.small_font.render("Hall of Fame", True, (220, 240, 255))
            self.screen.blit(lb_text, (self.home_lb_rect.x + (self.home_lb_rect.width // 2 - lb_text.get_width() // 2),
                                       self.home_lb_rect.y + (self.home_lb_rect.height // 2 - lb_text.get_height() // 2)))
            # Settings Button (Arcade Pill Style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.home_settings_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.home_settings_rect, 2, border_radius=16)
            settings_text = self.small_font.render("Settings", True, (220, 240, 255))
            self.screen.blit(settings_text, (self.home_settings_rect.x + (self.home_settings_rect.width // 2 - settings_text.get_width() // 2),
                                             self.home_settings_rect.y + (self.home_settings_rect.height // 2 - settings_text.get_height() // 2)))
            # Logout / Quit Button (Arcade Pill Style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.home_logout_rect, border_radius=16)
            pygame.draw.rect(self.screen, (100, 160, 220), self.home_logout_rect, 2, border_radius=16)
            lo_text = self.small_font.render("Quit", True, (220, 240, 255))
            self.screen.blit(lo_text, (self.home_logout_rect.x + (self.home_logout_rect.width // 2 - lo_text.get_width() // 2),
                                       self.home_logout_rect.y + (self.home_logout_rect.height // 2 - lo_text.get_height() // 2)))
        # --- SHIP SELECT SCREEN ---
        elif self.game_state == "ship_select":
            title_text = self.big_font.render("CHOOSE SHIP", True, (255, 255, 255))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 70))

            # Ship 1 Box
            c1 = (50, 180, 50) if self.selected_ship == "default" else (60, 60, 100)
            pygame.draw.rect(self.screen, c1, self.ship1_rect, 3, border_radius=6)
            if self.ship1_img:
                self.screen.blit(self.ship1_img, (self.ship1_rect.x + self.ship1_rect.width // 2 - 32, self.ship1_rect.y + 15))
            s1_text = self.small_font.render("DEFAULT", True, (255, 255, 255))
            self.screen.blit(s1_text, (self.ship1_rect.x + (self.ship1_rect.width // 2 - s1_text.get_width() // 2), self.ship1_rect.y + 90))

            # Ship 2 Box
            c2 = (50, 180, 50) if self.selected_ship == "advanced" else (60, 60, 100)
            pygame.draw.rect(self.screen, c2, self.ship2_rect, 3, border_radius=6)
            if self.ship2_img:
                self.screen.blit(self.ship2_img, (self.ship2_rect.x + self.ship2_rect.width // 2 - 32, self.ship2_rect.y + 15))
            s2_text = self.small_font.render("ADVANCED", True, (255, 255, 255))
            self.screen.blit(s2_text, (self.ship2_rect.x + (self.ship2_rect.width // 2 - s2_text.get_width() // 2), self.ship2_rect.y + 90))

            # Back Button
            pygame.draw.rect(self.screen, (150, 50, 50), self.ship_back_rect, border_radius=4)
            b_text = self.font.render("BACK", True, (255, 255, 255))
            self.screen.blit(b_text, (self.ship_back_rect.x + (self.ship_back_rect.width // 2 - b_text.get_width() // 2),
                                      self.ship_back_rect.y + (self.ship_back_rect.height // 2 - b_text.get_height() // 2)))

        # --- PLAYING / BLINKING ---
        elif self.game_state == "playing" or self.game_state == "blinking":
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            if self.bullet:
                self.bullet.draw(self.screen)
            if self.settings.get("mobile_controls", False):
                self.buttons.draw(self.screen)
                
            # 1. Draw Level (Top Left)
            level_text = self.font.render(f"Level: {getattr(self, 'level', 1)}", True, (255, 255, 100))
            self.screen.blit(level_text, (20, 20))

            # 2. Draw Score (Below Level)
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (20, 50))

            # 3. Draw Pause Button "II" (Top Right)
            self.pause_button_rect = pygame.Rect(self.screen_width - 60, 20, 40, 40)
            pygame.draw.rect(self.screen, (50, 50, 80), self.pause_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (150, 150, 200), self.pause_button_rect, 2, border_radius=8)

            pause_symbol = self.font.render("II", True, (255, 255, 255))
            self.screen.blit(pause_symbol, (self.pause_button_rect.x + (self.pause_button_rect.width - pause_symbol.get_width()) // 2, 
                                             self.pause_button_rect.y + (self.pause_button_rect.height - pause_symbol.get_height()) // 2))

        # --- PAUSE MENU SCREEN ---
        elif self.game_state == "paused":
            # Semi-transparent dark background overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Pause Title
            paused_title = self.big_font.render("GAME PAUSED", True, (255, 255, 255))
            self.screen.blit(paused_title, (self.screen_width // 2 - paused_title.get_width() // 2, 120))

            # Button layout positions
            menu_y = 220
            self.resume_button_rect = pygame.Rect(self.screen_width // 2 - 100, menu_y, 200, 50)
            self.restart_button_rect = pygame.Rect(self.screen_width // 2 - 100, menu_y + 70, 200, 50)
            self.home_button_rect = pygame.Rect(self.screen_width // 2 - 100, menu_y + 140, 200, 50)

            # 1. Continue Button (Arrow)
            pygame.draw.rect(self.screen, (50, 150, 50), self.resume_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 255, 100), self.resume_button_rect, 2, border_radius=10)
            resume_text = self.font.render("Continue", True, (255, 255, 255))
            self.screen.blit(resume_text, (self.resume_button_rect.x + (self.resume_button_rect.width - resume_text.get_width()) // 2,
                                           self.resume_button_rect.y + (self.resume_button_rect.height - resume_text.get_height()) // 2))

            # 2. Restart Button
            pygame.draw.rect(self.screen, (150, 100, 50), self.restart_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 180, 100), self.restart_button_rect, 2, border_radius=10)
            restart_text = self.font.render("Restart", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.restart_button_rect.x + (self.restart_button_rect.width - restart_text.get_width()) // 2,
                                            self.restart_button_rect.y + (self.restart_button_rect.height - restart_text.get_height()) // 2))

            # 3. Home Button
            pygame.draw.rect(self.screen, (50, 100, 200), self.home_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, (100, 180, 255), self.home_button_rect, 2, border_radius=10)
            home_text = self.font.render("Home", True, (255, 255, 255))
            self.screen.blit(home_text, (self.home_button_rect.x + (self.home_button_rect.width - home_text.get_width()) // 2,
                                         self.home_button_rect.y + (self.home_button_rect.height - home_text.get_height()) // 2))

       # --- GAME OVER ---
        elif self.game_state == "game_over":
            go_text = self.big_font.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(go_text, (self.screen_width // 2 - go_text.get_width() // 2, self.screen_height // 2 - 140))

            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score_text, (self.screen_width // 2 - final_score_text.get_width() // 2, self.screen_height // 2 - 80))

            # Play Again Button (Rounded dark-blue pill style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.reload_button_rect, border_radius=18)
            pygame.draw.rect(self.screen, (100, 150, 220), self.reload_button_rect, width=2, border_radius=18)
            btn_text = self.font.render("PLAY AGAIN", True, (255, 255, 255))
            self.screen.blit(btn_text, (self.reload_button_rect.x + (self.reload_button_rect.width // 2 - btn_text.get_width() // 2),
                                        self.reload_button_rect.y + (self.reload_button_rect.height // 2 - btn_text.get_height() // 2)))

            # Leaderboard Button (Rounded dark-blue pill style)
            pygame.draw.rect(self.screen, (25, 45, 85), self.leaderboard_button_rect, border_radius=18)
            pygame.draw.rect(self.screen, (100, 150, 220), self.leaderboard_button_rect, width=2, border_radius=18)
            lb_btn_text = self.font.render("LEADERBOARD", True, (255, 255, 255))
            self.screen.blit(lb_btn_text, (self.leaderboard_button_rect.x + (self.leaderboard_button_rect.width // 2 - lb_btn_text.get_width() // 2),
                                           self.leaderboard_button_rect.y + (self.leaderboard_button_rect.height // 2 - lb_btn_text.get_height() // 2)))
        # --- LEADERBOARD ---
        elif self.game_state == "leaderboard":
            title_text = self.big_font.render("LEADERBOARD", True, (255, 215, 0))
            self.screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 40))

            top_scores = get_leaderboard(5)
            y_offset = 140
            for i, row in enumerate(top_scores):
                rank_surf = self.font.render(f"{i+1}.", True, (255, 255, 255))
                name_surf = self.font.render(f"{row['username']}", True, (255, 255, 255))
                score_surf = self.font.render(f"{row['score']}", True, (255, 255, 255))

                self.screen.blit(rank_surf, (self.screen_width // 2 - 180, y_offset))
                self.screen.blit(name_surf, (self.screen_width // 2 - 110, y_offset))
                self.screen.blit(score_surf, (self.screen_width // 2 + 100 - score_surf.get_width(), y_offset))
                
                y_offset += 45

            pygame.draw.rect(self.screen, (150, 50, 50), self.back_button_rect)
            back_text = self.font.render("BACK", True, (255, 255, 255))
            self.screen.blit(back_text, (self.back_button_rect.x + (self.back_button_rect.width // 2 - back_text.get_width() // 2),
                                         self.back_button_rect.y + (self.back_button_rect.height // 2 - back_text.get_height() // 2)))

    def check_collisions(self):
        player_rect = self.player.get_rect()
        for enemy in self.enemies:
            if enemy.state == "offscreen":
                continue
            enemy_rect = enemy.get_rect()
            if player_rect.colliderect(enemy_rect):
                self.game_state = "blinking"
                self.player.is_blinking = True
                self.state_timer = 0
                return
            if self.bullet and self.bullet.get_rect().colliderect(enemy_rect):
                self.bullet = None
                enemy.health -= 1
                if enemy.health <= 0:
                    enemy.state = "offscreen"
                    self.score += 1
                break
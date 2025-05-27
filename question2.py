import pygame
import sys
import random

pygame.init()

# Declare screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scrolling Game")

# Declare all colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (150, 150, 150) 
SKIN_COLOR = (255, 224, 189)

# Declare game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
GAME_WON = 3 # New state for winning
LEVEL_COMPLETED = 4 # New state for level completion

# Declare global variables
game_state = MENU
score = 0
current_level_index = 0
level_data = []

# Declare fonts for text in the game
font = pygame.font.Font(None, 36)
medium_font = pygame.font.Font(None, 48)
large_font = pygame.font.Font(None, 72)

# Class for the main character which is humanly shaped in the game.
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_character(self.image, BLUE) # Draw the character onto the surface
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.jump_power = -20 
        self.y_velocity = 0
        self.is_jumping = False
        self.health = 100
        self.max_health = 100
        self.lives = 3
        self.direction = 1  # 1 for right, -1 for left
        self.projectiles = pygame.sprite.Group()
        self.invincible_timer = 0 
        self.invincible_duration = 90 

    def draw_character(self, surface, body_color):
        """Draws a human-like character onto the given surface with more detail."""
        surface.fill((0, 0, 0, 0))
        
        # Draw head circular shape
        head_radius = self.width // 3
        head_center_x = self.width // 2
        head_center_y = head_radius + 2 # Slightly lower for neck space
        pygame.draw.circle(surface, SKIN_COLOR, (head_center_x, head_center_y), head_radius)

        # Neck
        neck_width = self.width * 0.2
        neck_height = self.height * 0.05
        neck_x = (self.width - neck_width) // 2
        neck_y = head_center_y + head_radius - 2
        pygame.draw.rect(surface, SKIN_COLOR, (neck_x, neck_y, neck_width, neck_height))

        
        torso_width = self.width * 0.7
        torso_height = self.height * 0.3
        torso_x = (self.width - torso_width) // 2
        torso_y = neck_y + neck_height
        pygame.draw.rect(surface, body_color, (torso_x, torso_y, torso_width, torso_height))

        # Two Arms
        arm_width = self.width * 0.15
        arm_height = self.height * 0.3
        arm_y = torso_y + 5 # Start slightly below shoulder
        
        # Left arm
        pygame.draw.rect(surface, body_color, (torso_x - arm_width, arm_y, arm_width, arm_height))
        # Right arm
        pygame.draw.rect(surface, body_color, (torso_x + torso_width, arm_y, arm_width, arm_height))

        # Hands just small circle
        hand_radius = 4
        pygame.draw.circle(surface, SKIN_COLOR, (torso_x - arm_width + arm_width // 2, arm_y + arm_height), hand_radius)
        pygame.draw.circle(surface, SKIN_COLOR, (torso_x + torso_width + arm_width // 2, arm_y + arm_height), hand_radius)


        # Hips
        pelvis_width = self.width * 0.8
        pelvis_height = self.height * 0.1
        pelvis_x = (self.width - pelvis_width) // 2
        pelvis_y = torso_y + torso_height
        pygame.draw.rect(surface, body_color, (pelvis_x, pelvis_y, pelvis_width, pelvis_height))

        # Legs
        leg_segment_width = pelvis_width // 2 - 4 # Account for gap
        leg_segment_height = self.height * 0.2
        
        # Left thigh
        thigh_y = pelvis_y + pelvis_height
        pygame.draw.rect(surface, body_color, (pelvis_x, thigh_y, leg_segment_width, leg_segment_height))
        # Right thigh
        pygame.draw.rect(surface, body_color, (pelvis_x + pelvis_width - leg_segment_width, thigh_y, leg_segment_width, leg_segment_height))

        # Left shin
        shin_y = thigh_y + leg_segment_height
        pygame.draw.rect(surface, body_color, (pelvis_x, shin_y, leg_segment_width, leg_segment_height))
        # Right shin
        pygame.draw.rect(surface, body_color, (pelvis_x + pelvis_width - leg_segment_width, shin_y, leg_segment_width, leg_segment_height))

        # Feet
        foot_width = leg_segment_width + 2
        foot_height = 5
        foot_y = shin_y + leg_segment_height
        pygame.draw.rect(surface, BLACK, (pelvis_x, foot_y, foot_width, foot_height))
        pygame.draw.rect(surface, BLACK, (pelvis_x + pelvis_width - foot_width, foot_y, foot_width, foot_height))


        # Face details        
        pygame.draw.circle(surface, BLACK, (head_center_x - head_radius // 2, head_center_y - head_radius // 4), 2)
        pygame.draw.circle(surface, BLACK, (head_center_x + head_radius // 2, head_center_y - head_radius // 4), 2)
        pygame.draw.line(surface, BLACK, (head_center_x - head_radius // 3, head_center_y + head_radius // 4), (head_center_x + head_radius // 3, head_center_y + head_radius // 4), 1)
    
    def update(self, platforms):
        self.y_velocity += 0.7
        self.rect.y += self.y_velocity

        # Check for collision
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_velocity > 0: # Falling
                    self.rect.bottom = platform.rect.top
                    self.is_jumping = False
                    self.y_velocity = 0
                elif self.y_velocity < 0: # Jumping up
                    self.rect.top = platform.rect.bottom
                    self.y_velocity = 0

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Update timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Update projectiles
        self.projectiles.update()

    def move(self, dx):
        self.rect.x += dx * self.speed
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1

    def jump(self):
        if not self.is_jumping:
            self.y_velocity = self.jump_power
            self.is_jumping = True

    def shoot(self):
        # Create a new projectile
        projectile = Projectile(self.rect.centerx, self.rect.centery - 10, self.direction)
        self.projectiles.add(projectile)

    def take_damage(self, damage):
        if self.invincible_timer == 0:
            self.health -= damage
            self.invincible_timer = self.invincible_duration
            if self.health <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.health = self.max_health # Reset health for next life
                else:
                    return True # Player is dead
        return False # Player is not dead

    def draw(self, screen):
        if self.invincible_timer > 0 and (self.invincible_timer // 10) % 2 == 0:
            # Create a flashing image by drawing a red version
            flashing_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.draw_character(flashing_image, RED) # Use RED for flashing
            screen.blit(flashing_image, self.rect)
        else:
            screen.blit(self.image, self.rect)
        
        # Draw health bar
        health_bar_width = self.rect.width
        health_bar_height = 5
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y - 10
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        current_health_width = (self.health / self.max_health) * health_bar_width
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, current_health_width, health_bar_height))

        # Draw projectiles
        self.projectiles.draw(screen)
        

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.radius = 5
        self.color = YELLOW
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 * direction
        self.damage = 10

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
  

# Class for the enemy in the game.
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="normal"):
        super().__init__()
        self.enemy_type = enemy_type
        if self.enemy_type == "normal":
            self.width = 50
            self.height = 50
            self.health = 50
            self.speed = 2
            self.damage = 20
            self.color = RED # Enemy body color
        elif self.enemy_type == "boss":
            self.width = 100
            self.height = 100
            self.health = 300
            self.speed = 1
            self.damage = 40
            self.color = PURPLE 
        
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_character(self.image, self.color) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_health = self.health
        self.direction = 1 # 1 for right, -1 for left (for patrolling)
        
    def draw_character(self, surface, body_color):
        """Draws a human-like enemy onto the given surface with more detail."""
        surface.fill((0, 0, 0, 0))

       # Draw head circular shape
        head_radius = self.width // 3
        head_center_x = self.width // 2
        head_center_y = head_radius + 2
        pygame.draw.circle(surface, GRAY, (head_center_x, head_center_y), head_radius) # Enemy head color

        # Neck 
        neck_width = self.width * 0.2
        neck_height = self.height * 0.05
        neck_x = (self.width - neck_width) // 2
        neck_y = head_center_y + head_radius - 2
        pygame.draw.rect(surface, GRAY, (neck_x, neck_y, neck_width, neck_height))

        torso_width = self.width * 0.7
        torso_height = self.height * 0.3
        torso_x = (self.width - torso_width) // 2
        torso_y = neck_y + neck_height
        pygame.draw.rect(surface, body_color, (torso_x, torso_y, torso_width, torso_height))

        # Arms
        arm_width = self.width * 0.15
        arm_height = self.height * 0.3
        arm_y = torso_y + 5
        
        # Left arm
        pygame.draw.rect(surface, body_color, (torso_x - arm_width, arm_y, arm_width, arm_height))
        # Right arm
        pygame.draw.rect(surface, body_color, (torso_x + torso_width, arm_y, arm_width, arm_height))

        # Hands (small circles)
        hand_radius = 4
        pygame.draw.circle(surface, GRAY, (torso_x - arm_width + arm_width // 2, arm_y + arm_height), hand_radius)
        pygame.draw.circle(surface, GRAY, (torso_x + torso_width + arm_width // 2, arm_y + arm_height), hand_radius)

        # Hips
        pelvis_width = self.width * 0.8
        pelvis_height = self.height * 0.1
        pelvis_x = (self.width - pelvis_width) // 2
        pelvis_y = torso_y + torso_height
        pygame.draw.rect(surface, body_color, (pelvis_x, pelvis_y, pelvis_width, pelvis_height))

        # Legs (two rectangles for thighs and shins)
        leg_segment_width = pelvis_width // 2 - 4
        leg_segment_height = self.height * 0.2
        
        # Left thigh
        thigh_y = pelvis_y + pelvis_height
        pygame.draw.rect(surface, body_color, (pelvis_x, thigh_y, leg_segment_width, leg_segment_height))
        # Right thigh - FIX: Changed 'pelvel_x' to 'pelvis_x'
        pygame.draw.rect(surface, body_color, (pelvis_x + pelvis_width - leg_segment_width, thigh_y, leg_segment_width, leg_segment_height))

        # Left shin
        shin_y = thigh_y + leg_segment_height
        pygame.draw.rect(surface, body_color, (pelvis_x, shin_y, leg_segment_width, leg_segment_height))
        # Right shin
        pygame.draw.rect(surface, body_color, (pelvis_x + pelvis_width - leg_segment_width, shin_y, leg_segment_width, leg_segment_height))

        # Feet 
        foot_width = leg_segment_width + 2
        foot_height = 5
        foot_y = shin_y + leg_segment_height
        pygame.draw.rect(surface, BLACK, (pelvis_x, foot_y, foot_width, foot_height))
        pygame.draw.rect(surface, BLACK, (pelvis_x + pelvis_width - foot_width, foot_y, foot_width, foot_height))

        # Face details
        pygame.draw.line(surface, BLACK, (head_center_x - head_radius // 3, head_center_y - head_radius // 4), (head_center_x + head_radius // 3, head_center_y - head_radius // 4), 2) # Frowning eyes
        pygame.draw.line(surface, BLACK, (head_center_x - head_radius // 3, head_center_y + head_radius // 4), (head_center_x + head_radius // 3, head_center_y + head_radius // 4), 1) # Simple mouth


    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        
        # Check if enemy hits screen edges or platform edges
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1 # Change direction
            self.rect.x += self.speed * self.direction * 2 # Move a bit to avoid sticking

        self.rect.y += 2 
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True 
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Draw health bar for enemy
        health_bar_width = self.rect.width
        health_bar_height = 5
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y - 10
        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        current_health_width = (self.health / self.max_health) * health_bar_width
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, current_health_width, health_bar_height))


class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, collectible_type):
        super().__init__()
        self.collectible_type = collectible_type
        self.image = pygame.Surface((30, 30))
        if self.collectible_type == "health_boost":
            self.image.fill(GREEN)
            self.value = 25 # Health restored
        elif self.collectible_type == "extra_life":
            self.image.fill(ORANGE)
            self.value = 1 # Extra life
        elif self.collectible_type == "score_boost":
            self.image.fill(YELLOW)
            self.value = 50 # Score added
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Class for platform
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
level_data = [
    # Level 1
    {
        "platforms": [
            Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40), # Ground
            Platform(150, SCREEN_HEIGHT - 150, 200, 20),
            Platform(450, SCREEN_HEIGHT - 250, 150, 20),
            Platform(0, SCREEN_HEIGHT - 350, 100, 20),
            Platform(600, SCREEN_HEIGHT - 400, 200, 20),
        ],
        "enemies": [
            Enemy(200, SCREEN_HEIGHT - 90),
            Enemy(500, SCREEN_HEIGHT - 300),
        ],
        "collectibles": [
            Collectible(100, SCREEN_HEIGHT - 70, "health_boost"),
            Collectible(500, SCREEN_HEIGHT - 70, "score_boost"),
        ],
        "boss": None
    },
    # Level 2
    {
        "platforms": [
            Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40), # Ground
            Platform(100, SCREEN_HEIGHT - 120, 150, 20),
            Platform(300, SCREEN_HEIGHT - 200, 200, 20),
            Platform(550, SCREEN_HEIGHT - 120, 150, 20),
            Platform(200, SCREEN_HEIGHT - 300, 100, 20),
            Platform(400, SCREEN_HEIGHT - 400, 150, 20),
        ],
        "enemies": [
            Enemy(150, SCREEN_HEIGHT - 170),
            Enemy(400, SCREEN_HEIGHT - 250),
            Enemy(600, SCREEN_HEIGHT - 170),
        ],
        "collectibles": [
            Collectible(200, SCREEN_HEIGHT - 70, "score_boost"),
            Collectible(600, SCREEN_HEIGHT - 70, "health_boost"),
            Collectible(450, SCREEN_HEIGHT - 450, "extra_life"),
        ],
        "boss": None
    },
    # Level 3 (Boss Level)
    {
        "platforms": [
            Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40), # Ground
            Platform(SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT - 200, 200, 20),
            Platform(50, SCREEN_HEIGHT - 350, 100, 20),
            Platform(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 350, 100, 20),
        ],
        "enemies": [], # No normal enemies, only boss
        "collectibles": [
            Collectible(100, SCREEN_HEIGHT - 70, "health_boost"),
            Collectible(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 70, "health_boost"),
        ],
        "boss": Enemy(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT - 150, "boss")
    },
]

# Initialize the game
def init_game():
    global player, platforms, enemies, collectibles, score, current_level_index, game_state

    player = Player(50, SCREEN_HEIGHT - 100)
    score = 0
    current_level_index = 0
    load_level(current_level_index)
    game_state = PLAYING 

def load_level(level_idx):
    global platforms, enemies, collectibles, player
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    level = level_data[level_idx]

    for platform_obj in level["platforms"]:
        platforms.add(platform_obj)
    for enemy_obj in level["enemies"]:
        enemies.add(enemy_obj)
    for collectible_obj in level["collectibles"]:
        collectibles.add(collectible_obj)
    if level["boss"]:
        enemies.add(level["boss"]) # Add boss to enemies group

    player.rect.x = 50
    player.rect.y = SCREEN_HEIGHT - 100
    player.y_velocity = 0
    player.is_jumping = False
    
    # Handles the quitting of the game
def show_end_screen(win_state):
    global game_state
    SCREEN.fill(BLACK)

    if win_state == GAME_WON:
        main_text = large_font.render("CONGRATULATIONS!", True, GREEN)
        sub_text = font.render("You completed all levels!", True, WHITE)
    else: # GAME_OVER
        main_text = large_font.render("GAME OVER", True, RED)
        sub_text = font.render("Better luck next time!", True, WHITE)
    
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press 'R' to Restart", True, WHITE)
    quit_text = font.render("Press 'Q' to Quit", True, WHITE)


    main_rect = main_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))


    SCREEN.blit(main_text, main_rect)
    SCREEN.blit(sub_text, sub_rect)
    SCREEN.blit(score_text, score_rect)
    SCREEN.blit(restart_text, restart_rect)
    SCREEN.blit(quit_text, quit_rect)
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting_for_input = False
                    init_game() # Restart the game
                    game_state = PLAYING # Set game state back to playing
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Handles the congratulation after completing level of the game
def show_level_completed_screen():
    global game_state, current_level_index
    SCREEN.fill(BLACK)

    level_completed_text = large_font.render(f"Level {current_level_index} Completed!", True, GREEN)
    score_text = font.render(f"Score: {score}", True, WHITE)

    level_completed_rect = level_completed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))

    SCREEN.blit(level_completed_text, level_completed_rect)
    SCREEN.blit(score_text, score_rect)

    # Draw Continue Button
    continue_button_width = 200
    continue_button_height = 60
    continue_button_x = (SCREEN_WIDTH - continue_button_width) // 2
    continue_button_y = SCREEN_HEIGHT // 2 + 80
    continue_button_rect = pygame.Rect(continue_button_x, continue_button_y, continue_button_width, continue_button_height)
    
    pygame.draw.rect(SCREEN, BLUE, continue_button_rect, border_radius=10)
    pygame.draw.rect(SCREEN, WHITE, continue_button_rect, 3, border_radius=10) # Border

    continue_text = medium_font.render("CONTINUE", True, BLACK)
    continue_text_rect = continue_text.get_rect(center=continue_button_rect.center)
    SCREEN.blit(continue_text, continue_text_rect)

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting_for_input = False
                    load_level(current_level_index)
                    game_state = PLAYING
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button_rect.collidepoint(event.pos):
                    waiting_for_input = False
                    load_level(current_level_index)
                    game_state = PLAYING



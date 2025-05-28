# Initialize Pygame library modules to prepare for rendering graphics, managing events, and handling media
import pygame
import sys
import random

pygame.init()

# Set fixed dimensions for the main game window, ensuring a consistent rendering resolution across devices
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scrolling Game")

# Define RGB tuples representing a diverse color palette used for character rendering and UI elements
WHITE = (255, 255, 255)      # Used for backgrounds or neutral UI elements
BLACK = (0, 0, 0)            # Commonly used for outlines, shadows, or facial features
RED = (255, 0, 0)            # Often signifies danger or health reduction
GREEN = (0, 255, 0)          # Typically used to indicate health or environmental elements
BLUE = (0, 0, 255)           # Used for the default player avatar or cool thematic elements
YELLOW = (255, 255, 0)       # Eye-catching hue for highlights or interactive objects
ORANGE = (255, 165, 0)       # Used for warm-toned characters or visual emphasis
PURPLE = (128, 0, 128)       # Could represent magical elements or secondary enemies
BROWN = (139, 69, 19)        # Useful for terrain, platforms, or earthy tones
GRAY = (150, 150, 150)       # Used for neutral platforms or inactive UI
SKIN_COLOR = (255, 224, 189) # Realistic tone for humanoid character features

# Enumerate various discrete states of the game using integer constants for clarity and control flow handling
MENU = 0                # Main screen where players can start the game or configure settings
PLAYING = 1             # Active gameplay loop where interactions and logic are continuously updated
GAME_OVER = 2           # Triggered when player loses all lives or fails the mission
GAME_WON = 3            # A final win condition where objectives are successfully met
LEVEL_COMPLETED = 4     # Transitional state between levels for feedback or story advancement

# Initialize key global variables to track progression, state management, and level configurations
game_state = MENU                 # Current execution state of the game loop
score = 0                         # Accumulative metric tracking the player’s in-game success
current_level_index = 0          # Determines which level data is currently being rendered
level_data = []                  # Placeholder for level-specific configuration and platform data

# Load font resources from system with fallback to default if unavailable, used for HUD and game messages
font = pygame.font.Font(None, 36)        # Default small text (e.g., score, labels)
medium_font = pygame.font.Font(None, 48) # Medium emphasis text (e.g., menus, subtitles)
large_font = pygame.font.Font(None, 72)  # Primary headers or alerts (e.g., "Game Over")

# Define the Player class inheriting from pygame's Sprite to leverage built-in collision and grouping features
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Create a transparent image for drawing
        self.draw_character(self.image, BLUE)  # Render the visual representation of the character
        self.rect = self.image.get_rect(topleft=(x, y))  # Define collision box positioned at (x, y)

        # Movement and physics-related properties
        self.speed = 5                    # Horizontal traversal velocity (pixels per frame)
        self.jump_power = -20            # Upward impulse applied during jump events
        self.y_velocity = 0              # Vertical momentum, influenced by gravity and collisions
        self.is_jumping = False          # Flag to prevent double jumps until grounded

        # Survival and combat attributes
        self.health = 100                # Current health value, affected by damage
        self.max_health = 100            # Maximum allowable health
        self.lives = 3                   # Number of retries before game over

        # Directional orientation (1 = right, -1 = left), useful for animations or projectile spawning
        self.direction = 1

        # Container for projectiles instantiated by the player, allowing centralized update/render management
        self.projectiles = pygame.sprite.Group()

        # Timer for temporary invincibility (e.g., after taking damage) to prevent immediate re-hits
        self.invincible_timer = 0
        self.invincible_duration = 90    # Duration in frames (e.g., 1.5 seconds at 60 FPS)

    def draw_character(self, surface, body_color):
        """Dynamically draws a humanoid sprite onto the provided surface using geometric primitives."""
        surface.fill((0, 0, 0, 0))  # Clear surface with full transparency

        # === Head and facial features ===
        head_radius = self.width // 3
        head_center_x = self.width // 2
        head_center_y = head_radius + 2  # Slight offset downward to allocate space for neck
        pygame.draw.circle(surface, SKIN_COLOR, (head_center_x, head_center_y), head_radius)

        # === Neck ===
        neck_width = self.width * 0.2
        neck_height = self.height * 0.05
        neck_x = (self.width - neck_width) // 2
        neck_y = head_center_y + head_radius - 2
        pygame.draw.rect(surface, SKIN_COLOR, (neck_x, neck_y, neck_width, neck_height))

        # === Torso ===
        torso_width = self.width * 0.7
        torso_height = self.height * 0.3
        torso_x = (self.width - torso_width) // 2
        torso_y = neck_y + neck_height
        pygame.draw.rect(surface, body_color, (torso_x, torso_y, torso_width, torso_height))

        # === Arms ===
        arm_width = self.width * 0.15
        arm_height = self.height * 0.3
        arm_y = torso_y + 5  # Slight offset for anatomical realism

        # Left and right arms
        pygame.draw.rect(surface, body_color, (torso_x - arm_width, arm_y, arm_width, arm_height))
        pygame.draw.rect(surface, body_color, (torso_x + torso_width, arm_y, arm_width, arm_height))

        # === Hands (simple circular palms) ===
        hand_radius = 4
        pygame.draw.circle(surface, SKIN_COLOR, (torso_x - arm_width + arm_width // 2, arm_y + arm_height), hand_radius)
        pygame.draw.circle(surface, SKIN_COLOR, (torso_x + torso_width + arm_width // 2, arm_y + arm_height), hand_radius)

        # === Pelvis ===
        pelvis_width = self.width * 0.8
        pelvis_height = self.height * 0.1
        pelvis_x = (self.width - pelvis_width) // 2
        pelvis_y = torso_y + torso_height
        pygame.draw.rect(surface, body_color, (pelvis_x, pelvis_y, pelvis_width, pelvis_height))

        # === Legs ===
        leg_segment_width = pelvis_width // 2 - 4
        leg_segment_height = self.height * 0.2

        # Thighs
        thigh_y = pelvis_y + pelvis_height
        pygame.draw.rect(surface, body_color, (pelvis_x, thigh_y, leg_segment_width, leg_segment_height))
        pygame.draw.rect(surface, body_color, (pelvis_x + pelvis_width - leg_segment_width, thigh_y, leg_segment_width, leg_segment_height))

        # Shins
        shin_y = thigh_y + leg_segment_height
        pygame.draw.rect(surface, body_color, (pelvis_x, shin_y, leg_segment_width, leg_segment_height))
        pygame.draw.rect(surface, body_color, (pelvis_x + pelvis_width - leg_segment_width, shin_y, leg_segment_width, leg_segment_height))

        # === Feet (stabilizing black rectangles) ===
        foot_width = leg_segment_width + 2
        foot_height = 5
        foot_y = shin_y + leg_segment_height
        pygame.draw.rect(surface, BLACK, (pelvis_x, foot_y, foot_width, foot_height))
        pygame.draw.rect(surface, BLACK, (pelvis_x + pelvis_width - foot_width, foot_y, foot_width, foot_height))

        # === Facial Details (basic cartoon-style eyes and mouth) ===
        pygame.draw.circle(surface, BLACK, (head_center_x - head_radius // 2, head_center_y - head_radius // 4), 2)
        pygame.draw.circle(surface, BLACK, (head_center_x + head_radius // 2, head_center_y - head_radius // 4), 2)
        pygame.draw.line(surface, BLACK, (head_center_x - head_radius // 3, head_center_y + head_radius // 4), (head_center_x + head_radius // 3, head_center_y + head_radius // 4), 1)

    def update(self, platforms):
        # Apply gravity-like acceleration to simulate falling
        self.y_velocity += 0.7
        self.rect.y += self.y_velocity

        # Collision detection and resolution with platforms (only in vertical direction)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_velocity > 0:  # Downward collision (landing)
                    self.rect.bottom = platform.rect.top
                    self.is_jumping = False
                    self.y_velocity = 0
                elif self.y_velocity < 0:  # Upward collision (head hits ceiling)
                    self.rect.top = platform.rect.bottom
                    self.y_velocity = 0

        # Constrain horizontal movement within screen boundaries
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


def game_loop():
    global game_state, score, current_level_index

    clock = pygame.time.Clock()
    running = True

    start_button_width = 200
    start_button_height = 60
    start_button_x = (SCREEN_WIDTH - start_button_width) // 2
    start_button_y = SCREEN_HEIGHT // 2 + 180
    start_button_rect = pygame.Rect(start_button_x, start_button_y, start_button_width, start_button_height)

    menu_player_display = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 80)
    menu_player_display.draw_character(menu_player_display.image, BLUE)


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.K_ESCAPE: 
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == PLAYING:
                    if event.key == pygame.K_LEFT:
                        pass 
                    if event.key == pygame.K_RIGHT:
                        pass
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    if event.key == pygame.K_f: # 'F' for Fire
                        player.shoot()
                elif game_state == MENU:
                    if event.key == pygame.K_RETURN: # Enter to start
                        init_game() 
                elif game_state == GAME_OVER or game_state == GAME_WON: 
                    if event.key == pygame.K_r:
                        init_game()
                        game_state = PLAYING
                    elif event.key == pygame.K_q:
                        running = False 
                elif game_state == LEVEL_COMPLETED:
                    if event.key == pygame.K_RETURN: 
                        load_level(current_level_index)
                        game_state = PLAYING
            
          
            if game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    init_game()

        if game_state == MENU:
            SCREEN.fill(BLACK)
            title_text = large_font.render("The Jumper's Journey", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
            SCREEN.blit(title_text, title_rect)

            # Display Instructions
            instructions = [
                "To Start the Game: Click 'Start' or Press ENTER",
                "To Move Left: Press the LEFT ARROW key",
                "To Move Right: Press the RIGHT ARROW key",
                "To Jump: Press the SPACEBAR",
                "To Shoot: Press the F key",
                "To Restart (Game Over/Won): Press the R key",
                "To Quit (Game Over/Won): Press the Q key"
            ]
            y_offset = -120
            for instruction in instructions:
                inst_text = font.render(instruction, True, WHITE)
                inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
                SCREEN.blit(inst_text, inst_rect)
                y_offset += 30

            # Draw Start Button
            pygame.draw.rect(SCREEN, GREEN, start_button_rect, border_radius=10)
            pygame.draw.rect(SCREEN, WHITE, start_button_rect, 3, border_radius=10) # Border

            start_text = medium_font.render("START GAME", True, BLACK)
            start_text_rect = start_text.get_rect(center=start_button_rect.center)
            SCREEN.blit(start_text, start_text_rect)    

            pygame.display.flip()

        elif game_state == PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move(-1)
            if keys[pygame.K_RIGHT]:
                player.move(1)

            player.update(platforms)
            enemies.update(platforms)

            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                if player.invincible_timer == 0:
                    if player.take_damage(enemy.damage):
                        
                        if player.lives <= 0:
                            game_state = GAME_OVER
                        else:
                            load_level(current_level_index) 
                        break 

            for projectile in player.projectiles:
                hit_enemies = pygame.sprite.spritecollide(projectile, enemies, False)
                for enemy in hit_enemies:
                    projectile.kill() 
                    if enemy.take_damage(projectile.damage):
                        score += 100 
                        enemy.kill()
                        if enemy.enemy_type == "boss":
                          
                            current_level_index += 1
                            if current_level_index < len(level_data):
                                game_state = LEVEL_COMPLETED 
                            else:
                                game_state = GAME_WON # Set to GAME_WON state
                                break
                if game_state == GAME_WON or game_state == LEVEL_COMPLETED: 
                    break 

            if game_state == GAME_WON or game_state == GAME_OVER or game_state == LEVEL_COMPLETED:
                continue       
            for collectible in pygame.sprite.spritecollide(player, collectibles, True): # True to remove collectible
                if collectible.collectible_type == "health_boost":
                    player.health = min(player.max_health, player.health + collectible.value)
                    score += 20
                elif collectible.collectible_type == "extra_life":
                    player.lives += collectible.value
                    score += 50
                elif collectible.collectible_type == "score_boost":
                    score += collectible.value

    
            level_completed_this_frame = False
            if current_level_index < len(level_data): 
                if not enemies: 
                    if level_data[current_level_index]["boss"] is not None:
                        level_completed_this_frame = True
                    else:
                        level_completed_this_frame = True
            
            if level_completed_this_frame:
                current_level_index += 1
                if current_level_index < len(level_data):
                    game_state = LEVEL_COMPLETED 
                else:
                    game_state = GAME_WON
                continue 


            SCREEN.fill(BLACK) # Clear screen

            platforms.draw(SCREEN)
            collectibles.draw(SCREEN)
            enemies.draw(SCREEN)
            player.draw(SCREEN)


            # Display UI
            score_text = font.render(f"Score: {score}", True, WHITE)
            health_text = font.render(f"Health: {player.health}", True, WHITE)
            lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
            level_text = font.render(f"Level: {current_level_index + 1}", True, WHITE)

            SCREEN.blit(score_text, (10, 10))
            SCREEN.blit(health_text, (10, 40))
            SCREEN.blit(lives_text, (10, 70))
            SCREEN.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 10, 10))

            pygame.display.flip()

            
            if player.rect.top > SCREEN_HEIGHT:
                if player.take_damage(player.max_health): 
                    if player.lives <= 0:
                        game_state = GAME_OVER
                    else:
                        load_level(current_level_index) 
                if game_state == GAME_OVER:
                    continue

            
            if player.lives <= 0:
                game_state = GAME_OVER
               
                continue 


        elif game_state == GAME_OVER:
            show_end_screen(GAME_OVER) 
        elif game_state == GAME_WON:
            show_end_screen(GAME_WON) 
        elif game_state == LEVEL_COMPLETED:
            show_level_completed_screen()


        clock.tick(60) 
    pygame.quit()
    sys.exit()
    

if __name__ == "__main__":
    game_loop()



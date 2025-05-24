import pygame
import sys
import random

# Initialize the game
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
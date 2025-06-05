import pygame
import numpy as np
import random
import cv2
import mediapipe as mp
import sys
import time
import os

# Initialize Pygame
pygame.init()

# Set up the Pygame window
window_width, window_height = 800, 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Kill the VC - Hand Gesture Game")

# Initialize Pygame mixer
pygame.mixer.init()

# Load fonts
title_font = pygame.font.SysFont("Arial", 64, bold=True)
menu_font = pygame.font.SysFont("Arial", 36)
font = pygame.font.SysFont("Arial", 24)

# Game states
MENU = 0
GAME = 1
GAME_OVER = 2
INSTRUCTIONS = 3
CALIBRATION = 4
LEVEL_SELECT = 5
VICTORY = 6

# Current game state
game_state = MENU

# Current level
current_level = 1
max_level = 3

# Open the webcam when needed
video = None

# Create assets directory if it doesn't exist
os.makedirs("assets/Assets", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

# Load background images for different levels
try:
    background_img = pygame.image.load("assets/Assets/gringotts.jpg")
    background_img = pygame.transform.scale(background_img, (window_width, window_height))
    
    # Create fallback backgrounds for other levels if not found
    try:
        background_img_level2 = pygame.image.load("assets/Assets/level2_bg.jpg")
        background_img_level2 = pygame.transform.scale(background_img_level2, (window_width, window_height))
    except:
        background_img_level2 = pygame.Surface((window_width, window_height))
        background_img_level2.fill((0, 50, 50))  # Teal background for level 2
        
    try:
        background_img_level3 = pygame.image.load("assets/Assets/level3_bg.jpg")
        background_img_level3 = pygame.transform.scale(background_img_level3, (window_width, window_height))
    except:
        background_img_level3 = pygame.Surface((window_width, window_height))
        background_img_level3.fill((50, 0, 50))  # Purple background for level 3
except:
    # Create fallback backgrounds if images not found
    background_img = pygame.Surface((window_width, window_height))
    background_img.fill((0, 0, 50))  # Dark blue background for level 1
    
    background_img_level2 = pygame.Surface((window_width, window_height))
    background_img_level2.fill((0, 50, 50))  # Teal background for level 2
    
    background_img_level3 = pygame.Surface((window_width, window_height))
    background_img_level3.fill((50, 0, 50))  # Purple background for level 3

# Dictionary to store level backgrounds
level_backgrounds = {
    1: background_img,
    2: background_img_level2,
    3: background_img_level3
}

# Load spaceship image
try:
    spaceship_img = pygame.image.load("assets/Assets/spaceship1-removebg-preview.png").convert_alpha()
    spaceship_width, spaceship_height = 100, 100
    spaceship_img = pygame.transform.scale(spaceship_img, (spaceship_width, spaceship_height))
    
    # Create enhanced spaceships for higher levels
    try:
        spaceship_img_level2 = pygame.image.load("assets/Assets/spaceship2.png").convert_alpha()
        spaceship_img_level2 = pygame.transform.scale(spaceship_img_level2, (spaceship_width, spaceship_height))
    except:
        # Create a level 2 spaceship with blue glow
        spaceship_img_level2 = spaceship_img.copy()
        glow = pygame.Surface((spaceship_width+20, spaceship_height+20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (0, 0, 255, 128), (0, 0, spaceship_width+20, spaceship_height+20))
        glow.blit(spaceship_img, (10, 10))
        spaceship_img_level2 = glow
        
    try:
        spaceship_img_level3 = pygame.image.load("assets/Assets/spaceship3.png").convert_alpha()
        spaceship_img_level3 = pygame.transform.scale(spaceship_img_level3, (spaceship_width, spaceship_height))
    except:
        # Create a level 3 spaceship with red glow
        spaceship_img_level3 = spaceship_img.copy()
        glow = pygame.Surface((spaceship_width+20, spaceship_height+20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 0, 0, 128), (0, 0, spaceship_width+20, spaceship_height+20))
        glow.blit(spaceship_img, (10, 10))
        spaceship_img_level3 = glow
except:
    # Create a fallback spaceship if image not found
    spaceship_img = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.polygon(spaceship_img, (200, 200, 200), [(50, 0), (0, 100), (100, 100)])
    
    # Create fallback enhanced spaceships
    spaceship_img_level2 = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.polygon(spaceship_img_level2, (100, 200, 255), [(50, 0), (0, 100), (100, 100)])
    
    spaceship_img_level3 = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.polygon(spaceship_img_level3, (255, 100, 100), [(50, 0), (0, 100), (100, 100)])

# Dictionary to store level spaceships
level_spaceships = {
    1: spaceship_img,
    2: spaceship_img_level2,
    3: spaceship_img_level3
}

# Load laser image
try:
    laser_img = pygame.image.load("assets/Assets/laser.png").convert_alpha()
    laser_width, laser_height = 20, 40
    laser_img = pygame.transform.scale(laser_img, (laser_width, laser_height))
    
    # Create enhanced lasers for higher levels
    try:
        laser_img_level2 = pygame.image.load("assets/Assets/laser2.png").convert_alpha()
        laser_img_level2 = pygame.transform.scale(laser_img_level2, (laser_width, laser_height))
    except:
        # Create a blue laser for level 2
        laser_img_level2 = pygame.Surface((laser_width, laser_height), pygame.SRCALPHA)
        pygame.draw.rect(laser_img_level2, (0, 100, 255), (0, 0, laser_width, laser_height))
        
    try:
        laser_img_level3 = pygame.image.load("assets/Assets/laser3.png").convert_alpha()
        laser_img_level3 = pygame.transform.scale(laser_img_level3, (laser_width*1.5, laser_height))
    except:
        # Create a red laser for level 3
        laser_img_level3 = pygame.Surface((laser_width*1.5, laser_height), pygame.SRCALPHA)
        pygame.draw.rect(laser_img_level3, (255, 50, 50), (0, 0, laser_width*1.5, laser_height))
except:
    # Create fallback lasers if images not found
    laser_img = pygame.Surface((20, 40), pygame.SRCALPHA)
    pygame.draw.rect(laser_img, (255, 0, 0), (0, 0, 20, 40))
    
    laser_img_level2 = pygame.Surface((20, 40), pygame.SRCALPHA)
    pygame.draw.rect(laser_img_level2, (0, 100, 255), (0, 0, 20, 40))
    
    laser_img_level3 = pygame.Surface((30, 40), pygame.SRCALPHA)
    pygame.draw.rect(laser_img_level3, (255, 50, 50), (0, 0, 30, 40))

# Dictionary to store level lasers
level_lasers = {
    1: laser_img,
    2: laser_img_level2,
    3: laser_img_level3
}

# Load VC image
try:
    vc_img = pygame.image.load("assets/Assets/Vc-removebg-preview.png").convert_alpha()
    vc_width, vc_height = 100, 100
    vc_img = pygame.transform.scale(vc_img, (vc_width, vc_height))
    
    # Create enhanced VCs for higher levels
    try:
        vc_img_level2 = pygame.image.load("assets/Assets/vc2.png").convert_alpha()
        vc_img_level2 = pygame.transform.scale(vc_img_level2, (vc_width, vc_height))
    except:
        # Create a level 2 VC with blue tint
        vc_img_level2 = vc_img.copy()
        blue_tint = pygame.Surface((vc_width, vc_height), pygame.SRCALPHA)
        blue_tint.fill((0, 0, 255, 100))
        vc_img_level2.blit(blue_tint, (0, 0))
        
    try:
        vc_img_level3 = pygame.image.load("assets/Assets/vc3.png").convert_alpha()
        vc_img_level3 = pygame.transform.scale(vc_img_level3, (vc_width*1.2, vc_height*1.2))
    except:
        # Create a level 3 VC with red tint and larger size
        vc_img_level3 = pygame.transform.scale(vc_img, (int(vc_width*1.2), int(vc_height*1.2)))
        red_tint = pygame.Surface((int(vc_width*1.2), int(vc_height*1.2)), pygame.SRCALPHA)
        red_tint.fill((255, 0, 0, 100))
        vc_img_level3.blit(red_tint, (0, 0))
except:
    # Create fallback VCs if images not found
    vc_img = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(vc_img, (150, 150, 150), (50, 50), 50)
    
    vc_img_level2 = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(vc_img_level2, (100, 100, 200), (50, 50), 50)
    
    vc_img_level3 = pygame.Surface((120, 120), pygame.SRCALPHA)
    pygame.draw.circle(vc_img_level3, (200, 100, 100), (60, 60), 60)

# Dictionary to store level VCs
level_vcs = {
    1: vc_img,
    2: vc_img_level2,
    3: vc_img_level3
}

# Load sound effects
try:
    laser_sound = pygame.mixer.Sound("assets/Assets/Laserpm.wav")
    laser_sound.set_volume(0.3)
    
    # Create enhanced sounds for higher levels
    try:
        laser_sound_level2 = pygame.mixer.Sound("assets/Assets/laser2.wav")
        laser_sound_level2.set_volume(0.4)
    except:
        laser_sound_level2 = laser_sound
        
    try:
        laser_sound_level3 = pygame.mixer.Sound("assets/Assets/laser3.wav")
        laser_sound_level3.set_volume(0.5)
    except:
        laser_sound_level3 = laser_sound
        
    try:
        victory_sound = pygame.mixer.Sound("assets/Assets/victory.wav")
        victory_sound.set_volume(0.6)
    except:
        victory_sound = None
        
    try:
        level_up_sound = pygame.mixer.Sound("assets/Assets/levelup.wav")
        level_up_sound.set_volume(0.6)
    except:
        level_up_sound = None
except:
    laser_sound = None
    laser_sound_level2 = None
    laser_sound_level3 = None
    victory_sound = None
    level_up_sound = None

# Dictionary to store level laser sounds
level_laser_sounds = {
    1: laser_sound,
    2: laser_sound_level2,
    3: laser_sound_level3
}

# Try to load background music
try:
    pygame.mixer.music.load("assets/sounds/Joh F.mp4")
    has_music = True
    
    # Try to load additional music for different levels
    has_level_music = {
        1: True,
        2: False,
        3: False
    }
    
    try:
        level2_music = "assets/sounds/level2_music.mp3"
        pygame.mixer.music.load(level2_music)
        has_level_music[2] = True
    except:
        pass
        
    try:
        level3_music = "assets/sounds/level3_music.mp3"
        pygame.mixer.music.load(level3_music)
        has_level_music[3] = True
    except:
        pass
        
    # Reload default music
    pygame.mixer.music.load("assets/sounds/Joh F.mp4")
except:
    try:
        # Fallback to laser sound if main music not found
        pygame.mixer.music.load("assets/Assets/Laserpm.wav")
        has_music = True
        has_level_music = {1: True, 2: False, 3: False}
    except:
        print("Background music files not found. Continuing without music.")
        has_music = False
        has_level_music = {1: False, 2: False, 3: False}

# Level music paths
level_music = {
    1: "assets/sounds/Joh F.mp4",
    2: "assets/sounds/level2_music.mp3",
    3: "assets/sounds/level3_music.mp3"
}

# Game variables
spaceship_x = window_width // 2 - spaceship_width // 2
spaceship_y = window_height - spaceship_height
spaceship_speed = 5

laser_x, laser_y = None, None
laser_speed = 10
laser_state = "ready"
laser_count = 0
laser_cooldown = 0

enemies = []
num_enemies = 6
vc_index = 0
vc_health = 100
score = 0

# Level-specific variables
level_settings = {
    1: {
        "num_enemies": 6,
        "enemy_speed_range": (-2, 2),
        "laser_speed": 10,
        "vc_health": 100,
        "spaceship_speed": 5
    },
    2: {
        "num_enemies": 8,
        "enemy_speed_range": (-3, 3),
        "laser_speed": 12,
        "vc_health": 150,
        "spaceship_speed": 6
    },
    3: {
        "num_enemies": 10,
        "enemy_speed_range": (-4, 4),
        "laser_speed": 15,
        "vc_health": 200,
        "spaceship_speed": 7
    }
}

# Hand tracking variables
hand_area_threshold = 500  # Default value
mp_hands = None  # Initialize when needed

# Health bar properties
health_bar_width, health_bar_height = 200, 20
health_bar_x, health_bar_y = window_width // 2 - health_bar_width // 2, 10

# Function to initialize enemies based on current level
def initialize_enemies():
    global enemies, vc_index, num_enemies
    
    # Get level-specific settings
    level_config = level_settings[current_level]
    num_enemies = level_config["num_enemies"]
    enemy_speed_range = level_config["enemy_speed_range"]
    
    enemies = []
    for _ in range(num_enemies):
        enemy_x = np.random.randint(0, window_width - vc_width)
        enemy_y = np.random.randint(50, window_height // 2)
        enemy_speed_x = random.uniform(enemy_speed_range[0], enemy_speed_range[1])
        enemy_speed_y = random.uniform(enemy_speed_range[0]/2, enemy_speed_range[1]/2)
        enemy_rotation_speed = random.uniform(-5, 5)
        enemy_health = 100
        enemies.append((enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health))
    
    # Randomly select the real VC
    vc_index = random.randint(0, num_enemies - 1)

# Function to draw the health bar and score
def draw_health_bar():
    # Get level-specific settings
    level_config = level_settings[current_level]
    max_health = level_config["vc_health"]
    
    health_width = max(0, int((vc_health / max_health) * health_bar_width))
    pygame.draw.rect(screen, (255, 255, 255), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_width, health_bar_height))
    health_text = font.render(f"VC Health (Level {current_level})", True, (255, 255, 255))
    screen.blit(health_text, (health_bar_x + health_bar_width // 2 - health_text.get_width() // 2, 
                             health_bar_y + health_bar_height + 5))

def draw_score():
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    # Draw current level indicator
    level_text = font.render(f"Level: {current_level}/{max_level}", True, (255, 255, 255))
    screen.blit(level_text, (10, 40))

# Function to draw menu
def draw_menu():
    screen.blit(background_img, (0, 0))
    
    # Draw title
    title_text = title_font.render("KILL THE VC", True, (255, 0, 0))
    screen.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 100))
    
    # Draw subtitle
    subtitle_text = menu_font.render("Hand Gesture Space Game", True, (255, 255, 255))
    screen.blit(subtitle_text, (window_width // 2 - subtitle_text.get_width() // 2, 180))
    
    # Draw menu options
    play_text = menu_font.render("1. Play Game", True, (255, 255, 255))
    screen.blit(play_text, (window_width // 2 - play_text.get_width() // 2, 260))
    
    level_select_text = menu_font.render("2. Level Select", True, (255, 255, 255))
    screen.blit(level_select_text, (window_width // 2 - level_select_text.get_width() // 2, 300))
    
    instructions_text = menu_font.render("3. Instructions", True, (255, 255, 255))
    screen.blit(instructions_text, (window_width // 2 - instructions_text.get_width() // 2, 340))
    
    calibration_text = menu_font.render("4. Calibrate Hand Tracking", True, (255, 255, 255))
    screen.blit(calibration_text, (window_width // 2 - calibration_text.get_width() // 2, 380))
    
    quit_text = menu_font.render("5. Quit", True, (255, 255, 255))
    screen.blit(quit_text, (window_width // 2 - quit_text.get_width() // 2, 420))
    
    # Draw credits
    credits_text = font.render("Created by iman, Blackboyzeus, Potus", True, (200, 200, 200))
    screen.blit(credits_text, (window_width // 2 - credits_text.get_width() // 2, window_height - 40))

# Function to draw level select screen
def draw_level_select():
    screen.blit(background_img, (0, 0))
    
    title_text = menu_font.render("SELECT LEVEL", True, (255, 255, 255))
    screen.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 100))
    
    # Draw level options
    for i in range(1, max_level + 1):
        if i <= max(1, current_level):  # Only show unlocked levels
            level_text = menu_font.render(f"{i}. Level {i}", True, (255, 255, 255))
        else:
            level_text = menu_font.render(f"{i}. Level {i} (Locked)", True, (150, 150, 150))
        screen.blit(level_text, (window_width // 2 - level_text.get_width() // 2, 180 + (i-1) * 60))
    
    # Draw level descriptions
    level_descriptions = {
        1: "Standard mission: Defeat the VC in a basic environment",
        2: "Advanced mission: Faster enemies and stronger VC",
        3: "Expert mission: Maximum difficulty with elite enemies"
    }
    
    description_y = 350
    for i in range(1, max_level + 1):
        if i <= max(1, current_level):  # Only show descriptions for unlocked levels
            desc_text = font.render(level_descriptions[i], True, (200, 200, 200))
            screen.blit(desc_text, (window_width // 2 - desc_text.get_width() // 2, description_y))
            description_y += 30
    
    back_text = font.render("Press BACKSPACE to return to menu", True, (200, 200, 200))
    screen.blit(back_text, (window_width // 2 - back_text.get_width() // 2, window_height - 40))

# Function to draw instructions
def draw_instructions():
    screen.blit(background_img, (0, 0))
    
    title_text = menu_font.render("HOW TO PLAY", True, (255, 255, 255))
    screen.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 50))
    
    instructions = [
        "1. Position your hand in front of your webcam",
        "2. Move your hand to control the spaceship",
        "3. Press SPACEBAR to fire lasers",
        "4. Target the special VC enemy to win (marked with red circle)",
        "5. Avoid or destroy other enemies",
        "6. Reduce the VC's health to zero to advance to next level",
        "7. Complete all 3 levels to achieve total victory",
        "",
        "Press BACKSPACE to return to menu"
    ]
    
    for i, line in enumerate(instructions):
        line_text = font.render(line, True, (255, 255, 255))
        screen.blit(line_text, (window_width // 2 - line_text.get_width() // 2, 120 + i * 40))

# Function to draw calibration screen
def draw_calibration():
    global hand_area_threshold
    
    screen.blit(background_img, (0, 0))
    
    title_text = menu_font.render("HAND TRACKING CALIBRATION", True, (255, 255, 255))
    screen.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 50))
    
    # Draw current threshold value
    threshold_text = font.render(f"Current Threshold: {hand_area_threshold}", True, (255, 255, 255))
    screen.blit(threshold_text, (window_width // 2 - threshold_text.get_width() // 2, 120))
    
    # Draw instructions
    instructions = [
        "Use UP/DOWN arrow keys to adjust sensitivity",
        "Higher value = Less sensitive",
        "Lower value = More sensitive",
        "",
        "Move your hand to test the tracking",
        "Press ENTER to save and return to menu"
    ]
    
    for i, line in enumerate(instructions):
        line_text = font.render(line, True, (255, 255, 255))
        screen.blit(line_text, (window_width // 2 - line_text.get_width() // 2, 180 + i * 30))
    
    # If webcam is active, show hand tracking feedback
    if video:
        ret, frame = video.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mp_hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                index_finger_x = int(index_finger_tip.x * window_width)
                index_finger_y = int(index_finger_tip.y * window_height)
                
                # Draw a circle to show tracking
                pygame.draw.circle(screen, (255, 0, 0), (index_finger_x, index_finger_y), 10)
                
                # Show feedback text
                feedback_text = font.render("Hand detected!", True, (0, 255, 0))
                screen.blit(feedback_text, (window_width // 2 - feedback_text.get_width() // 2, 400))
            else:
                feedback_text = font.render("No hand detected. Show your hand to the camera.", True, (255, 0, 0))
                screen.blit(feedback_text, (window_width // 2 - feedback_text.get_width() // 2, 400))

# Function to draw victory screen
def draw_victory():
    screen.blit(background_img, (0, 0))
    
    victory_title = title_font.render("TOTAL VICTORY!", True, (255, 215, 0))
    screen.blit(victory_title, (window_width // 2 - victory_title.get_width() // 2, 100))
    
    victory_text = menu_font.render("You've defeated all VCs! Welcome to IPO", True, (255, 255, 255))
    screen.blit(victory_text, (window_width // 2 - victory_text.get_width() // 2, 200))
    
    score_text = menu_font.render(f"Final Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 260))
    
    continue_text = font.render("Press ENTER to return to menu or ESC to quit", True, (200, 200, 200))
    screen.blit(continue_text, (window_width // 2 - continue_text.get_width() // 2, 350))

# Function to start the game
def start_game(level=1):
    global game_state, video, mp_hands, vc_health, score, laser_state, laser_cooldown, current_level
    
    # Set the current level
    current_level = level
    
    # Get level-specific settings
    level_config = level_settings[current_level]
    vc_health = level_config["vc_health"]
    
    # Initialize game variables
    laser_state = "ready"
    laser_cooldown = 0
    
    # Initialize enemies
    initialize_enemies()
    
    # Initialize hand tracking if not already done
    if mp_hands is None:
        mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
    
    # Open webcam if not already open
    if video is None:
        video = cv2.VideoCapture(0)
    
    # Start background music if available
    if has_music:
        if has_level_music[current_level]:
            try:
                pygame.mixer.music.load(level_music[current_level])
                pygame.mixer.music.play(-1)
            except:
                # Fallback to default music
                pygame.mixer.music.load(level_music[1])
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.load(level_music[1])
            pygame.mixer.music.play(-1)
    
    # Change game state
    game_state = GAME

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Menu navigation
            if game_state == MENU:
                if event.key == pygame.K_1:
                    start_game(1)  # Start from level 1
                elif event.key == pygame.K_2:
                    game_state = LEVEL_SELECT
                elif event.key == pygame.K_3:
                    game_state = INSTRUCTIONS
                elif event.key == pygame.K_4:
                    # Initialize webcam and hand tracking for calibration
                    if video is None:
                        video = cv2.VideoCapture(0)
                    if mp_hands is None:
                        mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
                    game_state = CALIBRATION
                elif event.key == pygame.K_5 or event.key == pygame.K_ESCAPE:
                    running = False
            
            # Level select navigation
            elif game_state == LEVEL_SELECT:
                if event.key == pygame.K_1:
                    start_game(1)
                elif event.key == pygame.K_2 and current_level >= 1:
                    start_game(2)
                elif event.key == pygame.K_3 and current_level >= 2:
                    start_game(3)
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                    game_state = MENU
            
            # Return to menu from instructions
            elif game_state == INSTRUCTIONS:
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                    game_state = MENU
            
            # Calibration controls
            elif game_state == CALIBRATION:
                if event.key == pygame.K_UP:
                    hand_area_threshold += 50
                elif event.key == pygame.K_DOWN:
                    hand_area_threshold = max(50, hand_area_threshold - 50)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    game_state = MENU
            
            # Game controls
            elif game_state == GAME:
                if event.key == pygame.K_SPACE and laser_cooldown == 0:
                    if laser_state == "ready":
                        laser_x = spaceship_x + spaceship_width // 2 - laser_width // 2
                        laser_y = spaceship_y
                        laser_state = "fire"
                        
                        # Play level-specific laser sound
                        if level_laser_sounds[current_level]:
                            level_laser_sounds[current_level].play()
                            
                        laser_cooldown = 20
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    if has_music:
                        pygame.mixer.music.stop()
            
            # Game over screen
            elif game_state == GAME_OVER:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # If we completed the final level, go to victory screen
                    if current_level == max_level:
                        game_state = VICTORY
                        if victory_sound:
                            victory_sound.play()
                    else:
                        # Otherwise advance to the next level
                        current_level += 1
                        start_game(current_level)
                        if level_up_sound:
                            level_up_sound.play()
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    if has_music:
                        pygame.mixer.music.stop()
            
            # Victory screen
            elif game_state == VICTORY:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    game_state = MENU
                    if has_music:
                        pygame.mixer.music.stop()
                elif event.key == pygame.K_ESCAPE:
                    running = False
    
    # Handle different game states
    if game_state == MENU:
        draw_menu()
    
    elif game_state == LEVEL_SELECT:
        draw_level_select()
    
    elif game_state == INSTRUCTIONS:
        draw_instructions()
    
    elif game_state == CALIBRATION:
        draw_calibration()
    
    elif game_state == GAME:
        # Game logic
        ret, frame = video.read()
        
        if not ret:
            print("Failed to grab frame from camera")
            game_state = MENU
            continue
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = mp_hands.process(rgb_frame)
        
        # Get level-specific settings
        level_config = level_settings[current_level]
        laser_speed = level_config["laser_speed"]
        spaceship_speed = level_config["spaceship_speed"]
        
        # Draw background for current level
        screen.blit(level_backgrounds[current_level], (0, 0))
        
        # Handle hand tracking
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
            index_finger_x = int(index_finger_tip.x * window_width)
            index_finger_y = int(index_finger_tip.y * window_height)
            
            # Move spaceship based on hand position
            displacement_x = index_finger_x - (spaceship_x + spaceship_width // 2)
            displacement_y = index_finger_y - (spaceship_y + spaceship_height // 2)
            
            sensitivity = 0.1
            spaceship_x += int(displacement_x * sensitivity)
            spaceship_y -= int(displacement_y * sensitivity)
            
            # Keep spaceship within bounds
            spaceship_x = max(0, min(spaceship_x, window_width - spaceship_width))
            spaceship_y = max(window_height // 2, min(spaceship_y, window_height - spaceship_height))
        
        # Draw spaceship for current level
        screen.blit(level_spaceships[current_level], (spaceship_x, spaceship_y))
        
        # Handle laser
        if laser_state == "fire":
            screen.blit(level_lasers[current_level], (laser_x, laser_y))
            laser_y -= laser_speed
            if laser_y <= 0:
                laser_state = "ready"
        
        # Update and draw enemies
        for i, enemy in enumerate(enemies):
            enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health = enemy
            
            # Move enemy
            enemy_x += enemy_speed_x
            enemy_y += enemy_speed_y
            
            # Bounce off walls
            if enemy_x <= 0 or enemy_x >= window_width - vc_width:
                enemy_speed_x *= -1
            if enemy_y <= 0 or enemy_y >= window_height // 2 - vc_height:
                enemy_speed_y *= -1
            
            # Occasionally change direction
            if random.randint(1, 100) <= 1:
                enemy_speed_x = random.uniform(level_config["enemy_speed_range"][0], level_config["enemy_speed_range"][1])
                enemy_speed_y = random.uniform(level_config["enemy_speed_range"][0]/2, level_config["enemy_speed_range"][1]/2)
            
            # Draw enemy
            if i == vc_index:
                # Draw the main VC for current level
                screen.blit(level_vcs[current_level], (enemy_x, enemy_y))
                # Draw a subtle indicator for the real VC
                pygame.draw.circle(screen, (255, 0, 0, 128), 
                                  (int(enemy_x + vc_width // 2), int(enemy_y + vc_height // 2)), 
                                  int(vc_width // 2) + 5, 2)
            else:
                # Regular enemies are rotated
                rotated_enemy = pygame.transform.rotate(level_vcs[current_level], (enemy_rotation_speed * pygame.time.get_ticks() / 100) % 360)
                rotated_rect = rotated_enemy.get_rect(center=(enemy_x + vc_width // 2, enemy_y + vc_height // 2))
                screen.blit(rotated_enemy, rotated_rect.topleft)
            
            # Check for laser collision
            if laser_state == "fire":
                if (laser_x >= enemy_x and laser_x <= enemy_x + vc_width and 
                    laser_y >= enemy_y and laser_y <= enemy_y + vc_height):
                    # Hit!
                    laser_state = "ready"
                    
                    if i == vc_index:
                        # Hit the real VC
                        damage = 25 * current_level  # More damage in higher levels
                        vc_health -= damage
                        score += damage
                        # Visual feedback
                        pygame.draw.circle(screen, (255, 255, 0), 
                                          (int(enemy_x + vc_width // 2), int(enemy_y + vc_height // 2)), 
                                          50, 0)
                    else:
                        # Hit regular enemy
                        score += 5 * current_level
                        # Visual feedback
                        pygame.draw.circle(screen, (255, 255, 255), 
                                          (int(enemy_x + vc_width // 2), int(enemy_y + vc_height // 2)), 
                                          30, 0)
            
            # Update enemy
            enemy = (enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health)
            enemies[i] = enemy
        
        # Draw UI elements
        draw_health_bar()
        draw_score()
        
        # Check for victory
        if vc_health <= 0:
            game_state = GAME_OVER
            if has_music:
                pygame.mixer.music.stop()
        
        # Update laser cooldown
        if laser_cooldown > 0:
            laser_cooldown -= 1
    
    elif game_state == GAME_OVER:
        # Draw level completion screen
        screen.blit(level_backgrounds[current_level], (0, 0))
        
        if current_level < max_level:
            level_title = title_font.render(f"LEVEL {current_level} COMPLETE!", True, (255, 215, 0))
            screen.blit(level_title, (window_width // 2 - level_title.get_width() // 2, 100))
            
            next_level_text = menu_font.render(f"Get ready for Level {current_level + 1}", True, (255, 255, 255))
            screen.blit(next_level_text, (window_width // 2 - next_level_text.get_width() // 2, 200))
            
            score_text = menu_font.render(f"Current Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 260))
            
            continue_text = font.render("Press ENTER to continue or ESC to return to menu", True, (200, 200, 200))
            screen.blit(continue_text, (window_width // 2 - continue_text.get_width() // 2, 350))
        else:
            # Final level complete
            victory_title = title_font.render("FINAL LEVEL COMPLETE!", True, (255, 215, 0))
            screen.blit(victory_title, (window_width // 2 - victory_title.get_width() // 2, 100))
            
            victory_text = menu_font.render("You've defeated the final VC boss!", True, (255, 255, 255))
            screen.blit(victory_text, (window_width // 2 - victory_text.get_width() // 2, 200))
            
            score_text = menu_font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 260))
            
            continue_text = font.render("Press ENTER to see your victory or ESC to return to menu", True, (200, 200, 200))
            screen.blit(continue_text, (window_width // 2 - continue_text.get_width() // 2, 350))
    
    elif game_state == VICTORY:
        # Draw final victory screen
        draw_victory()
    
    # Update display
    pygame.display.update()
    clock.tick(60)

# Clean up
if video:
    video.release()
pygame.quit()
sys.exit()

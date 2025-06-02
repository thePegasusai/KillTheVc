import pygame
import numpy as np
import random
import cv2
import mediapipe as mp
import sys
import time

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

# Current game state
game_state = MENU

# Open the webcam when needed
video = None

# Load background image
try:
    background_img = pygame.image.load("assets/Assets/gringotts.jpg")
    background_img = pygame.transform.scale(background_img, (window_width, window_height))
except:
    # Create a fallback background if image not found
    background_img = pygame.Surface((window_width, window_height))
    background_img.fill((0, 0, 50))  # Dark blue background

# Load spaceship image
try:
    spaceship_img = pygame.image.load("assets/Assets/spaceship1-removebg-preview.png").convert_alpha()
    spaceship_width, spaceship_height = 100, 100
    spaceship_img = pygame.transform.scale(spaceship_img, (spaceship_width, spaceship_height))
except:
    # Create a fallback spaceship if image not found
    spaceship_img = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.polygon(spaceship_img, (200, 200, 200), [(50, 0), (0, 100), (100, 100)])

# Load laser image
try:
    laser_img = pygame.image.load("assets/Assets/laser.png").convert_alpha()
    laser_width, laser_height = 20, 40
    laser_img = pygame.transform.scale(laser_img, (laser_width, laser_height))
except:
    # Create a fallback laser if image not found
    laser_img = pygame.Surface((20, 40), pygame.SRCALPHA)
    pygame.draw.rect(laser_img, (255, 0, 0), (0, 0, 20, 40))

# Load VC image
try:
    vc_img = pygame.image.load("assets/Assets/Vc-removebg-preview.png").convert_alpha()
    vc_width, vc_height = 100, 100
    vc_img = pygame.transform.scale(vc_img, (vc_width, vc_height))
except:
    # Create a fallback VC if image not found
    vc_img = pygame.Surface((100, 100), pygame.SRCALPHA)
    pygame.draw.circle(vc_img, (150, 150, 150), (50, 50), 50)

# Load sound effects
try:
    laser_sound = pygame.mixer.Sound("assets/Assets/Laserpm.wav")
    laser_sound.set_volume(0.3)
except:
    laser_sound = None

# Try to load background music
try:
    pygame.mixer.music.load("assets/Assets/Laserpm.wav")
    has_music = True
except:
    print("Background music file not found. Continuing without music.")
    has_music = False

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

# Hand tracking variables
hand_area_threshold = 500  # Default value
mp_hands = None  # Initialize when needed

# Health bar properties
health_bar_width, health_bar_height = 200, 20
health_bar_x, health_bar_y = window_width // 2 - health_bar_width // 2, 10

# Function to initialize enemies
def initialize_enemies():
    global enemies, vc_index
    enemies = []
    for _ in range(num_enemies):
        enemy_x = np.random.randint(0, window_width - vc_width)
        enemy_y = np.random.randint(50, window_height // 2)
        enemy_speed_x = random.uniform(-2, 2)
        enemy_speed_y = random.uniform(-1, 1)
        enemy_rotation_speed = random.uniform(-5, 5)
        enemy_health = 100
        enemies.append((enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health))
    
    # Randomly select the real VC
    vc_index = random.randint(0, num_enemies - 1)

# Function to draw the health bar and score
def draw_health_bar():
    health_width = max(0, int((vc_health / 100) * health_bar_width))
    pygame.draw.rect(screen, (255, 255, 255), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_width, health_bar_height))
    health_text = font.render("VC Health", True, (255, 255, 255))
    screen.blit(health_text, (health_bar_x + health_bar_width // 2 - health_text.get_width() // 2, 
                             health_bar_y + health_bar_height + 5))

def draw_score():
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

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
    screen.blit(play_text, (window_width // 2 - play_text.get_width() // 2, 280))
    
    instructions_text = menu_font.render("2. Instructions", True, (255, 255, 255))
    screen.blit(instructions_text, (window_width // 2 - instructions_text.get_width() // 2, 330))
    
    calibration_text = menu_font.render("3. Calibrate Hand Tracking", True, (255, 255, 255))
    screen.blit(calibration_text, (window_width // 2 - calibration_text.get_width() // 2, 380))
    
    quit_text = menu_font.render("4. Quit", True, (255, 255, 255))
    screen.blit(quit_text, (window_width // 2 - quit_text.get_width() // 2, 430))
    
    # Draw credits
    credits_text = font.render("Created by iman, Blackboyzeus, Potus", True, (200, 200, 200))
    screen.blit(credits_text, (window_width // 2 - credits_text.get_width() // 2, window_height - 40))

# Function to draw instructions
def draw_instructions():
    screen.blit(background_img, (0, 0))
    
    title_text = menu_font.render("HOW TO PLAY", True, (255, 255, 255))
    screen.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 50))
    
    instructions = [
        "1. Position your hand in front of your webcam",
        "2. Move your hand to control the spaceship",
        "3. Press SPACEBAR to fire lasers",
        "4. Target the special VC enemy to win",
        "5. Avoid or destroy other enemies",
        "6. Reduce the VC's health to zero to win",
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

# Function to start the game
def start_game():
    global game_state, video, mp_hands, vc_health, score, laser_state, laser_cooldown
    
    # Initialize game variables
    vc_health = 100
    score = 0
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
                    start_game()
                elif event.key == pygame.K_2:
                    game_state = INSTRUCTIONS
                elif event.key == pygame.K_3:
                    # Initialize webcam and hand tracking for calibration
                    if video is None:
                        video = cv2.VideoCapture(0)
                    if mp_hands is None:
                        mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
                    game_state = CALIBRATION
                elif event.key == pygame.K_4 or event.key == pygame.K_ESCAPE:
                    running = False
            
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
                        if laser_sound:
                            laser_sound.play()
                        laser_cooldown = 20
                elif event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    if has_music:
                        pygame.mixer.music.stop()
            
            # Game over screen
            elif game_state == GAME_OVER:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    game_state = MENU
                elif event.key == pygame.K_ESCAPE:
                    running = False
    
    # Handle different game states
    if game_state == MENU:
        draw_menu()
    
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
        
        # Draw background
        screen.blit(background_img, (0, 0))
        
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
        
        # Draw spaceship
        screen.blit(spaceship_img, (spaceship_x, spaceship_y))
        
        # Handle laser
        if laser_state == "fire":
            screen.blit(laser_img, (laser_x, laser_y))
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
                enemy_speed_x = random.uniform(-2, 2)
                enemy_speed_y = random.uniform(-1, 1)
            
            # Draw enemy
            if i == vc_index:
                screen.blit(vc_img, (enemy_x, enemy_y))
                # Draw a subtle indicator for the real VC
                pygame.draw.circle(screen, (255, 0, 0, 128), 
                                  (int(enemy_x + vc_width // 2), int(enemy_y + vc_height // 2)), 
                                  int(vc_width // 2) + 5, 2)
            else:
                # Regular enemies are rotated
                rotated_enemy = pygame.transform.rotate(vc_img, (enemy_rotation_speed * pygame.time.get_ticks() / 100) % 360)
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
                        vc_health -= 25
                        score += 25
                        # Visual feedback
                        pygame.draw.circle(screen, (255, 255, 0), 
                                          (int(enemy_x + vc_width // 2), int(enemy_y + vc_height // 2)), 
                                          50, 0)
                    else:
                        # Hit regular enemy
                        score += 5
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
        # Draw victory screen
        screen.blit(background_img, (0, 0))
        
        victory_title = title_font.render("VICTORY!", True, (255, 215, 0))
        screen.blit(victory_title, (window_width // 2 - victory_title.get_width() // 2, 100))
        
        victory_text = menu_font.render("You destroyed the VC! Welcome to IPO", True, (255, 255, 255))
        screen.blit(victory_text, (window_width // 2 - victory_text.get_width() // 2, 200))
        
        score_text = menu_font.render(f"Final Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 260))
        
        continue_text = font.render("Press ENTER to return to menu or ESC to quit", True, (200, 200, 200))
        screen.blit(continue_text, (window_width // 2 - continue_text.get_width() // 2, 350))
    
    # Update display
    pygame.display.update()
    clock.tick(60)

# Clean up
if video:
    video.release()
pygame.quit()
sys.exit()

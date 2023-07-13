import pygame
import numpy as np
import random
import cv2
import mediapipe as mp

# Initialize Pygame
pygame.init()

# Set up the Pygame window
window_width, window_height = 800, 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Kill the VC - Hand Gesture Game")

# Open the webcam
video = cv2.VideoCapture(0)

# Initialize Pygame mixer
pygame.mixer.init()

# Load background image
background_img = pygame.image.load("SensoryLink/Project Thalamus/Gaming/gringotts.jpg")
background_img = pygame.transform.scale(background_img, (window_width, window_height))

# Load spaceship image
spaceship_img = pygame.image.load("SensoryLink/Project Thalamus/Gaming/spaceship1-removebg-preview.png").convert_alpha()
spaceship_width, spaceship_height = 100, 100
spaceship_img = pygame.transform.scale(spaceship_img, (spaceship_width, spaceship_height))

# Load laser image
laser_img = pygame.image.load("SensoryLink/Project Thalamus/Gaming/laser.png").convert_alpha()
laser_width, laser_height = 20, 40
laser_img = pygame.transform.scale(laser_img, (laser_width, laser_height))

# Load VC image
vc_img = pygame.image.load("SensoryLink/Project Thalamus/Gaming/Vc-removebg-preview.png").convert_alpha()
vc_width, vc_height = 100, 100
vc_img = pygame.transform.scale(vc_img, (vc_width, vc_height))

# Load font for victory message and score display
font = pygame.font.SysFont("Arial", 36)

# Set up spaceship position and speed
spaceship_x = window_width // 2 - spaceship_width // 2
spaceship_y = window_height - spaceship_height
spaceship_speed = 5

# Set up laser properties
laser_x, laser_y = None, None
laser_speed = 10
laser_state = "ready"
laser_count = 0

# Set up VC properties
enemies = []
num_enemies = 6

for _ in range(num_enemies):
    enemy_x = np.random.randint(0, window_width - vc_width)
    enemy_y = np.random.randint(window_height // 2, window_height - vc_height)
    enemy_speed_x = random.uniform(-2, 2)
    enemy_speed_y = random.uniform(-2, 2)
    enemy_rotation_speed = random.uniform(-5, 5)
    enemy_health = 100  # Initialize enemy health
    enemies.append((enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health))

# Randomly select the real VC
vc_index = random.randint(0, num_enemies - 1)
real_vc = enemies[vc_index]

# Set up hand area threshold
hand_area_threshold = 500  # Adjust this value based on your hand size

# Set up VC health
vc_health = 100

# Set up health bar properties
health_bar_width, health_bar_height = 200, 20
health_bar_x, health_bar_y = window_width // 2 - health_bar_width // 2, 10

# Set up score
score = 0

# Play background music
pygame.mixer.music.load("SensoryLink/Project Thalamus/Gaming/Joh F.mp4")
pygame.mixer.music.play(-1)  # Play the music in an infinite loop

# Initialize Mediapipe Hand module
mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Function to draw the health bar and score
def draw_health_bar():
    health_width = max(0, int((vc_health / 100) * health_bar_width))
    pygame.draw.rect(screen, (255, 255, 255), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (health_bar_x, health_bar_y, health_width, health_bar_height))

def draw_score():
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

# Game loop
running = True
victory = False
fire_laser = False
laser_cooldown = 0
while running:
    ret, frame = video.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = mp_hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        index_finger_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        index_finger_x = int(index_finger_tip.x * window_width)
        index_finger_y = int(index_finger_tip.y * window_height)

        displacement_x = index_finger_x - (spaceship_x + spaceship_width // 2)
        displacement_y = index_finger_y - (spaceship_y + spaceship_height // 2)

        sensitivity = 0.1
        spaceship_x += int(displacement_x * sensitivity)
        spaceship_y -= int(displacement_y * sensitivity)

        spaceship_x = max(0, min(spaceship_x, window_width - spaceship_width))
        spaceship_y = max(window_height // 2, min(spaceship_y, window_height - spaceship_height))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and laser_cooldown == 0:
            fire_laser = True
            laser_cooldown = 30  # Set a cooldown period for firing lasers
        else:
            fire_laser = False

        if fire_laser and laser_state == "ready":
            laser_x = spaceship_x + spaceship_width // 2 - laser_width // 2
            laser_y = spaceship_y
            laser_state = "fire"
            laser_count += 1

        if laser_count >= 3:
            laser_count = 0
            pygame.time.wait(1000)

    screen.blit(background_img, (0, 0))
    screen.blit(spaceship_img, (spaceship_x, spaceship_y))
    draw_health_bar()
    draw_score()

    for i, enemy in enumerate(enemies):
        enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health = enemy

        enemy_x += enemy_speed_x
        enemy_y += enemy_speed_y
        enemy_rotation_angle = (enemy_rotation_speed % 360)

        if enemy_x <= 0 or enemy_x >= window_width - vc_width or enemy_y <= 0 or enemy_y >= window_height // 2 - vc_height:
            enemy_x = np.random.randint(0, window_width - vc_width)
            enemy_y = np.random.randint(0, window_height // 2 - vc_height)
        
        if random.randint(1, 100) <= 5:
            enemy_speed_x = random.uniform(-2, 2)
            enemy_speed_y = random.uniform(-2, 2)
            enemy_rotation_speed = random.uniform(-5, 5)

        if i == vc_index:
            screen.blit(vc_img, (enemy_x, enemy_y))
        else:
            rotated_enemy = pygame.transform.rotate(vc_img, enemy_rotation_angle)
            screen.blit(rotated_enemy, (enemy_x, enemy_y))

        enemy = (enemy_x, enemy_y, enemy_speed_x, enemy_speed_y, enemy_rotation_speed, enemy_health)
        enemies[i] = enemy

    if laser_state == "fire":
        screen.blit(laser_img, (laser_x, laser_y))
        laser_y -= laser_speed
        if laser_y <= 0:
            laser_state = "ready"

    for i, enemy in enumerate(enemies):
        enemy_x, enemy_y, _, _, _, enemy_health = enemy

        if laser_state == "fire" and laser_x >= enemy_x and laser_x <= enemy_x + vc_width and laser_y >= enemy_y and laser_y <= enemy_y + vc_height:
            enemies[i] = (enemy_x, enemy_y, 0, 0, 0, enemy_health - 25)
            laser_state = "ready"
            score += 10

            if i == vc_index:
                vc_health -= 25

    # Check if VC health reaches zero
    if vc_health <= 0:
        victory = True
        running = False

    # Update the screen
    pygame.display.update()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if laser_cooldown > 0:
        laser_cooldown -= 1

# Game over loop
while victory:
    screen.blit(background_img, (0, 0))
    victory_text = font.render("You destroyed the VC! Welcome to IPO", True, (255, 255, 255))
    screen.blit(victory_text, (window_width // 2 - victory_text.get_width() // 2, window_height // 2 - victory_text.get_height() // 2))
    draw_score()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            victory = False

# Release the webcam and quit Pygame
video.release()
pygame.quit()

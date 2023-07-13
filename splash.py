import pygame
import subprocess
import sys

# Initialize Pygame
pygame.init()


# Set up the Pygame window
window_width, window_height = 800, 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Kill the VC - Hand Gesture Game")

# Load splash screen image
splash_img = pygame.image.load("SensoryLink/yolov7/Gaming/DALL·E 2023-06-04 09.22.14 - full body of a luxury space ship gundam in the modern era mid battle in space.jpg")
splash_img = pygame.transform.scale(splash_img, (window_width, window_height))

# Load font for play button and game description
font = pygame.font.SysFont("Arial", 36)
desc_font = pygame.font.SysFont("Arial", 24)

# Game write-up
game_writeup = [
    "Welcome to Kill the VC - Hand Gesture Game!",
    "In this game, you will use hand gestures to control a spaceship",
    "and destroy the enemy VC (Virtual Character).",
    "",  # Empty line for spacing
    "To control the spaceship, place your hand in front of the webcam",
    "and move your index finger to move the spaceship accordingly.",
    "",  # Empty line for spacing
    "Press and hold the Spacebar to fire laser shots and destroy the VC.",
    "But be careful! The VC will also try to attack you.",
    "",  # Empty line for spacing
    "Can you destroy the VC and emerge victorious? Play now to find out!",
]


def start_game():
    subprocess.call(["python3", "SensoryLink/yolov7/Gaming/game.py"])  # Start the game.py file

# Display splash screen
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the mouse click is within the bounds of the play button
            if play_button_rect.collidepoint(event.pos):
                start_game()  # Start the game by calling the start_game function

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw splash screen image
    screen.blit(splash_img, (0, 0))

    # Draw play button
    play_button_text = font.render("Play", True, (0, 0, 0))
    play_button_width, play_button_height = play_button_text.get_width() + 20, play_button_text.get_height() + 10
    play_button_x, play_button_y = window_width // 2 - play_button_width // 2, 20
    play_button_rect = pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)
    pygame.draw.rect(screen, (255, 255, 255), play_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), play_button_rect, 2)
    play_button_text_rect = play_button_text.get_rect(center=play_button_rect.center)
    screen.blit(play_button_text, play_button_text_rect)

    # Draw game write-up
    text_y = window_height // 2 - len(game_writeup) * 20 // 2
    for line in game_writeup:
        text = desc_font.render(line, True, (255, 255, 255))
        text_rect = text.get_rect(center=(window_width // 2, text_y))
        screen.blit(text, text_rect)
        text_y += 30

    pygame.display.update()

pygame.quit()
sys.exit()

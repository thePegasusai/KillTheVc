#!/usr/bin/env python3
"""
Standalone version of Kill the VC game
This version has minimal dependencies and focuses on window display
"""

import sys
import os
import time
import platform

# Set environment variables for display
if platform.system() == 'Darwin':  # macOS
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    os.environ['SDL_WINDOWID'] = '0'
    os.environ['SDL_VIDEO_CENTERED'] = '1'
elif platform.system() == 'Linux':
    os.environ['SDL_VIDEODRIVER'] = 'x11'
    os.environ['SDL_VIDEO_CENTERED'] = '1'
elif platform.system() == 'Windows':
    os.environ['SDL_VIDEODRIVER'] = 'windows'
    os.environ['SDL_VIDEO_CENTERED'] = '1'

# Try to import pygame
try:
    import pygame
except ImportError:
    print("ERROR: pygame module not found. Please install it with: pip install pygame")
    sys.exit(1)

# Initialize pygame
pygame.init()

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def main():
    """Main function with display focus"""
    print("Starting Kill the VC standalone game...")
    
    # Create the game window with multiple options to ensure it appears
    try:
        # Try to create window with default settings
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error:
        try:
            # Try with software rendering
            os.environ['SDL_VIDEODRIVER'] = 'software'
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error:
            try:
                # Try with a smaller window
                screen = pygame.display.set_mode((640, 480))
            except pygame.error:
                print("ERROR: Could not create game window with any method")
                return 1
    
    # Set window title and icon
    pygame.display.set_caption("Kill the VC")
    
    # Create a clock for controlling the frame rate
    clock = pygame.time.Clock()
    
    # Game variables
    running = True
    font = pygame.font.SysFont(None, 36)
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Fill the screen with a color
        screen.fill((0, 0, 50))  # Dark blue background
        
        # Draw text
        title_text = font.render("Kill the VC", True, WHITE)
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        instruction_text = font.render("Press ESC to quit", True, WHITE)
        screen.blit(instruction_text, (WINDOW_WIDTH // 2 - instruction_text.get_width() // 2, 200))
        
        # Draw a spaceship
        pygame.draw.polygon(screen, BLUE, [
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100),
            (WINDOW_WIDTH // 2 - 30, WINDOW_HEIGHT - 50),
            (WINDOW_WIDTH // 2 + 30, WINDOW_HEIGHT - 50)
        ])
        
        # Draw an enemy
        pygame.draw.rect(screen, RED, (WINDOW_WIDTH // 2 - 25, 150, 50, 50))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

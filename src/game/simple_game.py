#!/usr/bin/env python3
"""
Simple version of Kill the VC game
This version doesn't require webcam access and has minimal dependencies
"""

import sys
import os
import random
import time

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

# Game variables
score = 0
level = 1
game_over = False
victory = False

class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WINDOW_WIDTH // 2 - self.width // 2
        self.y = WINDOW_HEIGHT - self.height - 20
        self.speed = 8
        self.color = BLUE
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw a triangle on top to make it look like a spaceship
        pygame.draw.polygon(screen, WHITE, [
            (self.x + self.width // 2, self.y - 10),
            (self.x + 10, self.y),
            (self.x + self.width - 10, self.y)
        ])
        
    def move(self, direction):
        if direction == "left":
            self.x -= self.speed
        elif direction == "right":
            self.x += self.speed
            
        # Keep player within screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x > WINDOW_WIDTH - self.width:
            self.x = WINDOW_WIDTH - self.width

class Laser:
    def __init__(self, x, y):
        self.width = 5
        self.height = 20
        self.x = x
        self.y = y
        self.speed = 10
        self.color = GREEN
        self.active = True
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
    def move(self):
        self.y -= self.speed
        if self.y < 0:
            self.active = False

class Enemy:
    def __init__(self, is_vc=False):
        self.width = 40
        self.height = 40
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = random.randint(50, 200)
        self.speed_x = random.randint(-3, 3)
        if self.speed_x == 0:
            self.speed_x = 1
        self.speed_y = random.randint(1, 2)
        self.color = RED if is_vc else (150, 150, 150)
        self.is_vc = is_vc
        self.health = 100 if is_vc else 20
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.is_vc:
            # Draw health bar for VC
            pygame.draw.rect(screen, BLACK, (self.x, self.y - 10, self.width, 5))
            health_width = int((self.health / 100) * self.width)
            pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, 5))
            
            # Draw VC indicator
            pygame.draw.circle(screen, RED, (self.x + self.width // 2, self.y + self.height // 2), 
                              self.width // 2 + 5, 2)
        
    def move(self):
        self.x += self.speed_x
        
        # Bounce off walls
        if self.x <= 0 or self.x >= WINDOW_WIDTH - self.width:
            self.speed_x *= -1
            
        # Random vertical movement for non-VC enemies
        if not self.is_vc and random.randint(0, 100) < 5:
            self.y += self.speed_y
            
        # Keep enemies within top half of screen
        if self.y > WINDOW_HEIGHT // 2:
            self.y = WINDOW_HEIGHT // 2

def main():
    # Set up the game window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Kill the VC - Simple Mode")
    clock = pygame.time.Clock()
    
    # Create game objects
    player = Player()
    lasers = []
    
    # Create enemies
    enemies = []
    for i in range(5):
        enemies.append(Enemy(is_vc=(i == 0)))  # First enemy is the VC
    
    # Game loop
    global game_over, victory, score, level
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and not game_over:
                    # Fire laser
                    laser_x = player.x + player.width // 2 - 2
                    laser_y = player.y - 20
                    lasers.append(Laser(laser_x, laser_y))
                elif event.key == pygame.K_RETURN and (game_over or victory):
                    # Restart game
                    game_over = False
                    victory = False
                    score = 0
                    level = 1
                    player = Player()
                    lasers = []
                    enemies = []
                    for i in range(5):
                        enemies.append(Enemy(is_vc=(i == 0)))
        
        if not game_over and not victory:
            # Handle keyboard input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")
            
            # Update lasers
            for laser in lasers[:]:
                laser.move()
                if not laser.active:
                    lasers.remove(laser)
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.move()
                
                # Check for laser collisions
                for laser in lasers[:]:
                    if (laser.x >= enemy.x and laser.x <= enemy.x + enemy.width and
                        laser.y >= enemy.y and laser.y <= enemy.y + enemy.height):
                        # Hit!
                        if enemy.is_vc:
                            enemy.health -= 10
                            score += 10
                            if enemy.health <= 0:
                                enemies.remove(enemy)
                                # Check if all enemies are defeated
                                if not any(e.is_vc for e in enemies):
                                    if level < 3:
                                        # Advance to next level
                                        level += 1
                                        # Create new enemies for next level
                                        enemies = []
                                        for i in range(5 + level):
                                            enemies.append(Enemy(is_vc=(i == 0)))
                                            enemies[-1].speed_x *= level  # Faster enemies in higher levels
                                    else:
                                        # Victory!
                                        victory = True
                        else:
                            enemies.remove(enemy)
                            score += 5
                        
                        lasers.remove(laser)
                        break
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw player
        player.draw(screen)
        
        # Draw lasers
        for laser in lasers:
            laser.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw UI
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        level_text = font.render(f"Level: {level}/3", True, WHITE)
        screen.blit(level_text, (10, 50))
        
        # Draw game over or victory screen
        if game_over:
            game_over_text = font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, 
                                        WINDOW_HEIGHT // 2 - game_over_text.get_height() // 2))
            
            restart_text = font.render("Press ENTER to restart or ESC to quit", True, WHITE)
            screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 
                                      WINDOW_HEIGHT // 2 + 50))
        elif victory:
            victory_text = font.render("VICTORY! You defeated all VCs!", True, GREEN)
            screen.blit(victory_text, (WINDOW_WIDTH // 2 - victory_text.get_width() // 2, 
                                      WINDOW_HEIGHT // 2 - victory_text.get_height() // 2))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, 
                                         WINDOW_HEIGHT // 2 + 50))
            
            restart_text = font.render("Press ENTER to play again or ESC to quit", True, WHITE)
            screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, 
                                     WINDOW_HEIGHT // 2 + 100))
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())

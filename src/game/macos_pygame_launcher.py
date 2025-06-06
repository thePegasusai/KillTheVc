#!/usr/bin/env python3
"""
macOS-specific pygame launcher for Kill the VC
This launcher uses macOS-specific techniques to ensure the pygame window appears
"""

import sys
import os
import platform
import subprocess
import time
import traceback

# Set environment variables specifically for macOS
def set_macos_environment():
    """Set environment variables for optimal pygame window display on macOS"""
    print("Setting macOS-specific environment variables")
    
    # Force pygame to use the correct video driver
    os.environ['SDL_VIDEODRIVER'] = 'cocoa'
    
    # Force the window to appear in the foreground
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Set the window layer to be above other windows
    os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
    
    # Disable fullscreen optimization which can cause issues
    os.environ['SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS'] = '0'
    
    # Set the process to high priority
    os.environ['SDL_HINT_RENDER_VSYNC'] = '1'
    
    # Ensure the window is not minimized
    os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '0'
    
    # Force the window to be visible
    os.environ['SDL_VIDEO_X11_VISUALID'] = ''
    
    # Set the app name for macOS
    os.environ['SDL_VIDEO_X11_NET_WM_NAME'] = 'Kill the VC'
    
    # Additional macOS-specific settings
    if platform.system() == 'Darwin':
        # Use AppleScript to ensure the window comes to the foreground
        try:
            # Create an AppleScript to bring the window to the front
            script = '''
            tell application "System Events"
                set frontmost of every process whose unix id is {} to true
            end tell
            '''.format(os.getpid())
            
            # Execute the AppleScript
            subprocess.Popen(['osascript', '-e', script])
        except Exception as e:
            print(f"Failed to execute AppleScript: {e}")

def bring_window_to_front():
    """Use macOS-specific techniques to bring the window to the front"""
    if platform.system() == 'Darwin':
        try:
            # Create an AppleScript to bring the window to the front
            script = '''
            tell application "Python" to activate
            tell application "System Events"
                set frontmost of process "Python" to true
            end tell
            '''
            
            # Execute the AppleScript
            subprocess.Popen(['osascript', '-e', script])
        except Exception as e:
            print(f"Failed to bring window to front: {e}")

def run_game():
    """Run the game with special handling for macOS"""
    try:
        # Set macOS-specific environment variables
        set_macos_environment()
        
        # Try to import and run the game module
        try:
            # Add the current directory to the path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, script_dir)
            
            # Try to import the game module
            import game
            print("Game module imported successfully")
            return 0
        except ImportError as e:
            print(f"Could not import game module: {e}")
            
            # If import fails, try to run the standalone game
            try:
                # Try to import pygame
                import pygame
                pygame.init()
                
                # Try to import OpenCV
                try:
                    import cv2
                    print("OpenCV imported successfully")
                except ImportError:
                    print("OpenCV not available, running simplified game")
                
                # Create a window with specific flags for macOS
                screen = pygame.display.set_mode((800, 600), pygame.SHOWN)
                pygame.display.set_caption("Kill the VC")
                
                # Set the window icon
                try:
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    icon_path = os.path.join(script_dir, "assets", "Assets", "icon-removebg-preview.png")
                    if os.path.exists(icon_path):
                        icon = pygame.image.load(icon_path)
                        pygame.display.set_icon(icon)
                except Exception as e:
                    print(f"Failed to set icon: {e}")
                
                # Bring the window to the front
                bring_window_to_front()
                
                # Try to run the standalone game
                standalone_path = os.path.join(script_dir, "standalone_game.py")
                if os.path.exists(standalone_path):
                    print("Running standalone game...")
                    # Import the standalone game module
                    sys.path.insert(0, os.path.dirname(standalone_path))
                    standalone_name = os.path.basename(standalone_path).replace(".py", "")
                    standalone_module = __import__(standalone_name)
                    return 0
                
                # If standalone game is not available, run a simple game loop
                print("Running simple game loop...")
                clock = pygame.time.Clock()
                running = True
                background_color = (0, 0, 50)  # Dark blue background
                
                # Simple game objects
                player_x = 400
                player_y = 500
                player_speed = 5
                
                enemies = []
                for i in range(5):
                    enemies.append({
                        'x': 100 + i * 150,
                        'y': 100,
                        'speed': 2,
                        'direction': 1
                    })
                
                # Main game loop
                while running:
                    # Process events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                    
                    # Get keyboard input
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        player_x -= player_speed
                    if keys[pygame.K_RIGHT]:
                        player_x += player_speed
                    
                    # Keep player within bounds
                    player_x = max(50, min(player_x, 750))
                    
                    # Update enemies
                    for enemy in enemies:
                        enemy['x'] += enemy['speed'] * enemy['direction']
                        if enemy['x'] < 50 or enemy['x'] > 750:
                            enemy['direction'] *= -1
                    
                    # Draw everything
                    screen.fill(background_color)
                    
                    # Draw player (triangle spaceship)
                    pygame.draw.polygon(screen, (0, 200, 255), [
                        (player_x, player_y - 30),
                        (player_x - 20, player_y),
                        (player_x + 20, player_y)
                    ])
                    
                    # Draw enemies (red squares)
                    for enemy in enemies:
                        pygame.draw.rect(screen, (255, 0, 0), (enemy['x'] - 20, enemy['y'] - 20, 40, 40))
                    
                    # Draw title
                    font = pygame.font.SysFont(None, 48)
                    title = font.render("Kill the VC", True, (255, 255, 255))
                    screen.blit(title, (400 - title.get_width() // 2, 30))
                    
                    # Draw instructions
                    font = pygame.font.SysFont(None, 24)
                    instructions = font.render("Use arrow keys to move, ESC to quit", True, (255, 255, 255))
                    screen.blit(instructions, (400 - instructions.get_width() // 2, 70))
                    
                    # Update display
                    pygame.display.flip()
                    
                    # Cap the frame rate
                    clock.tick(60)
                
                # Clean up
                pygame.quit()
                return 0
            except Exception as e:
                print(f"Failed to run pygame: {e}")
                traceback.print_exc()
                return 1
    except Exception as e:
        print(f"Error running game: {e}")
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("Starting Kill the VC macOS pygame launcher...")
    
    # Print system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    
    # Run the game
    return run_game()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
PyQt5-based launcher for Kill the VC
This launcher creates a native window that will reliably display on macOS
"""

import sys
import os
import platform
import threading
import time
import traceback
import subprocess
import importlib.util

# Check if PyQt5 is installed, if not try to install it
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
except ImportError:
    print("PyQt5 not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QFont
    except Exception as e:
        print(f"Failed to install PyQt5: {e}")
        sys.exit(1)

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kill the VC")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2c3e50;")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # Add title label
        title_label = QLabel("Kill the VC")
        title_label.setStyleSheet("color: #3498db; font-size: 36px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add status label
        self.status_label = QLabel("Initializing game...")
        self.status_label.setStyleSheet("color: white; font-size: 18px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Add start button
        self.start_button = QPushButton("Start Game")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 18px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_button.setFixedSize(200, 50)
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)
        
        # Game state
        self.game_running = False
        self.game_thread = None
        
        # Start the game automatically after a short delay
        QTimer.singleShot(500, self.start_game)
    
    def start_game(self):
        """Start the game in a separate thread"""
        if self.game_running:
            return
        
        self.status_label.setText("Starting game...")
        self.start_button.setEnabled(False)
        
        # Start game in a separate thread
        self.game_thread = threading.Thread(target=self.run_game)
        self.game_thread.daemon = True
        self.game_thread.start()
    
    def run_game(self):
        """Run the actual game"""
        try:
            self.game_running = True
            
            # Update status
            self.status_label.setText("Game running...")
            
            # Try to import and run the game module
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # First try to import the game module
            try:
                # Add the current directory to the path
                sys.path.insert(0, script_dir)
                
                # Try to import the game module
                import game
                print("Game module imported successfully")
                return
            except ImportError as e:
                print(f"Could not import game module: {e}")
                
                # If import fails, try to run a simple pygame window
                try:
                    import pygame
                    pygame.init()
                    
                    # Create a window
                    screen = pygame.display.set_mode((800, 600))
                    pygame.display.set_caption("Kill the VC")
                    
                    # Game variables
                    clock = pygame.time.Clock()
                    running = True
                    background_color = (0, 0, 50)  # Dark blue
                    
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
                        
                        # Update display
                        pygame.display.flip()
                        
                        # Cap the frame rate
                        clock.tick(60)
                    
                    # Clean up
                    pygame.quit()
                    
                except Exception as e:
                    print(f"Failed to run pygame window: {e}")
                    traceback.print_exc()
                    
                    # If pygame fails, show a message in the PyQt window
                    self.status_label.setText(f"Error: {str(e)}")
            
            self.game_running = False
            self.start_button.setEnabled(True)
            
        except Exception as e:
            error_msg = f"Game error: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            self.game_running = False
            self.status_label.setText(error_msg)
            self.start_button.setEnabled(True)

def main():
    """Main function"""
    print("Starting Kill the VC PyQt5 launcher...")
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the game window
    window = GameWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

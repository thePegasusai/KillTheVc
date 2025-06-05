#!/usr/bin/env python3
"""
Tkinter launcher for Kill the VC
This launcher uses tkinter to create a reliable window on macOS
"""

import sys
import os
import platform
import subprocess
import threading
import time
import traceback

# Try to import tkinter
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    print("ERROR: tkinter not available. This is required for the game.")
    sys.exit(1)

# Try to import pygame
try:
    import pygame
except ImportError:
    print("ERROR: pygame not available. This is required for the game.")
    sys.exit(1)

class GameWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Kill the VC")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")
        
        # Center the window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Create a canvas for pygame rendering
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Initializing game...", fg="white", bg="#2c3e50", font=("Arial", 14))
        self.status_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Start button
        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game, bg="#2ecc71", fg="white", font=("Arial", 12), padx=20, pady=10)
        self.start_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        
        # Game state
        self.game_running = False
        self.game_thread = None
        
        # Initialize pygame in a separate thread
        self.init_thread = threading.Thread(target=self.initialize_pygame)
        self.init_thread.daemon = True
        self.init_thread.start()
        
        # Start the game automatically after a short delay
        self.root.after(1000, self.start_game)
    
    def initialize_pygame(self):
        """Initialize pygame in a separate thread"""
        try:
            # Initialize pygame
            pygame.init()
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Game engine initialized successfully!"))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
        except Exception as e:
            error_msg = f"Failed to initialize game engine: {str(e)}"
            self.root.after(0, lambda: self.status_label.config(text=error_msg))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
    
    def start_game(self):
        """Start the game in a separate thread"""
        if self.game_running:
            return
        
        self.status_label.config(text="Starting game...")
        self.start_button.config(state=tk.DISABLED)
        
        # Start game in a separate thread
        self.game_thread = threading.Thread(target=self.run_game)
        self.game_thread.daemon = True
        self.game_thread.start()
    
    def run_game(self):
        """Run the actual game"""
        try:
            self.game_running = True
            
            # Create a pygame window embedded in tkinter
            os.environ['SDL_WINDOWID'] = str(self.canvas.winfo_id())
            if platform.system() == "Darwin":  # macOS
                os.environ['SDL_VIDEODRIVER'] = 'windib'  # Try windib for macOS
            
            # Initialize pygame display
            pygame.display.init()
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
            self.game_running = False
            
            # Update UI
            self.root.after(0, lambda: self.status_label.config(text="Game ended"))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            
        except Exception as e:
            error_msg = f"Game error: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            self.game_running = False
            self.root.after(0, lambda: self.status_label.config(text=error_msg))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))

def main():
    """Main function"""
    print("Starting Kill the VC tkinter launcher...")
    
    # Create the root window
    root = tk.Tk()
    
    # Create the game window
    game_window = GameWindow(root)
    
    # Start the tkinter main loop
    root.mainloop()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
        
        # Show error in a message box
        try:
            import tkinter.messagebox
            tkinter.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        except:
            pass
        
        sys.exit(1)

#!/usr/bin/env python3
"""
Simple test script for pygame window display
This script tests if pygame can create a window on the current system
"""

import sys
import os
import platform
import time

# Print system information
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")

# Try different display methods
display_methods = ['', 'x11', 'cocoa', 'windib', 'directx', 'fbcon', 'dga', 'ggi', 'vgl', 'svgalib', 'aalib']

for method in display_methods:
    try:
        print(f"\nTrying display method: {method}")
        
        if method:
            os.environ['SDL_VIDEODRIVER'] = method
        
        # Import pygame
        import pygame
        pygame.init()
        
        # Create a window
        print("Creating window...")
        screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption(f"Test Window - {method or 'default'}")
        
        # Fill with a color
        screen.fill((0, 0, 128))
        pygame.display.flip()
        
        print(f"Window created successfully with method: {method or 'default'}")
        print("Window should be visible now. Press Ctrl+C to exit.")
        
        # Keep the window open
        running = True
        start_time = time.time()
        while running and time.time() - start_time < 5:  # Run for 5 seconds
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Draw something moving
            pygame.draw.circle(screen, (255, 255, 255), 
                              (int(320 + 100 * (time.time() % 2)), 240), 
                              30)
            pygame.display.flip()
            pygame.time.delay(100)
        
        # Clean up
        pygame.quit()
        
        print(f"Test completed successfully with method: {method or 'default'}")
        sys.exit(0)
    except Exception as e:
        print(f"Failed with method {method or 'default'}: {str(e)}")
        try:
            pygame.quit()
        except:
            pass

print("\nAll display methods failed. Please check your display settings.")
sys.exit(1)

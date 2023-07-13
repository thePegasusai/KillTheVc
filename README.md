# KillTheVc
Computer Vision Game 
Kill the VC - Hand Gesture Game

Welcome to Kill the VC, a hand gesture game where you destroy the VC (Venture Capitalist) and achieve victory! This game utilizes hand gestures captured through your webcam to control the spaceship and fire lasers. Your goal is to defeat the VC while avoiding other enemies. Let's get started!

Installation

To play Kill the VC, you need to follow these steps:

Install Python (version 3.7 or later) on your system.
Clone or download this repository to your local machine.
Navigate to the project directory using the command prompt or terminal.
Install the required dependencies by running the following command:
Copy code
pip install -r requirements.txt
Note: This game requires the installation of Pygame and other dependencies listed in the requirements.txt file.
replace the paths with correct paths from your own system.
How to Play

Once you have installed the necessary dependencies, follow these instructions to play Kill the VC:

Run the game by executing the Python script:
Copy code
python kill_the_vc.py
The game window will appear, displaying the spaceship and enemies.
Adjust the hand area threshold (variable hand_area_threshold) in the script to suit your hand size. This threshold determines the sensitivity of the hand movements.
Use your hand gestures to control the spaceship:
Place your hand in front of the webcam.
Move your hand to navigate the spaceship across the screen. The spaceship follows the movement of your index finger.
Use the spacebar to fire lasers. Each press of the spacebar fires one laser. There is a cooldown period between firing each laser.
Your objective is to destroy the VC (displayed as a special enemy) while avoiding the other enemies. Destroying the VC earns you points, and destroying regular enemies does not affect your score.
Keep an eye on your health bar and score displayed on the screen. The health bar represents the VC's health, and the score keeps track of your progress.
The game ends in victory when you destroy the VC. A victory message will be displayed on the screen.
To exit the game at any time, click the close button on the game window or press the "X" key.
License

This project is licensed under the MIT License.

Acknowledgements

The development of this game was made possible by the following libraries:

Pygame: A cross-platform set of Python modules designed for creating games.
NumPy: A powerful library for scientific computing and array manipulation.
OpenCV: A library for computer vision tasks, including image and video processing.
MediaPipe: A framework for building multimodal (e.g., video, audio) applied ML pipelines.
Author

This game was developed by [Your Name] as part of the SensoryLink/Project Thalamus project.

Enjoy playing Kill the VC and have fun defeating the enemies! Feel free to contribute to the project by submitting bug reports, feature requests, or pull requests. Happy gaming!

# Kill the VC - Hand Gesture Game

Welcome to Kill the VC, a thrilling hand gesture game where you battle against a fearsome Venture Capitalist (VC) using your very own spaceship!  Control your ship and unleash lasers with intuitive hand movements detected via your webcam.  Defeat the VC while dodging other enemies to claim victory!

## Installation

Follow these steps to get Kill the VC up and running on your system:

1.  **Install Python:**  Ensure you have Python 3.7 or later installed. You can download it from [python.org](https://www.python.org/downloads/).

2.  **Clone or Download:**  Obtain the game files by either cloning the Git repository (if available) or downloading the ZIP archive from your source (e.g., GitHub).

3.  **Navigate to Project Directory:** Open your command prompt or terminal and navigate to the directory where you extracted or cloned the game files.  For example:

    ```bash
    cd /path/to/kill_the_vc  # Replace with your actual path
    ```

4.  **Install Dependencies:**  Install the necessary Python packages using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

    This command will read the `requirements.txt` file and install all listed packages, including Pygame, NumPy, OpenCV, and MediaPipe.

    **Important Notes on Installation:**

    *   **`requirements.txt`:**  Make sure the `requirements.txt` file is in the same directory where you are running the `pip` command.
    *   **Possible Errors:** If you encounter errors during installation (e.g., related to OpenCV or MediaPipe), you may need to:
        *   Ensure you have the correct version of `pip` (try `python -m pip install --upgrade pip`).
        *   Consult the installation documentation for OpenCV or MediaPipe for specific platform requirements.  Some packages may require additional system-level dependencies.

## How to Play

1.  **Run the Game:** Execute the main Python script:

    ```bash
    python kill_the_vc.py
    ```

    This will launch the game window.

2.  **Hand Area Threshold (Calibration):**  Before you start, you might need to adjust the `hand_area_threshold` variable in the `kill_the_vc.py` script.  This value determines how sensitive the game is to your hand movements.

    *   **Finding the Value:** Open `kill_the_vc.py` in a text editor.  Locate the line that defines `hand_area_threshold`.
    *   **Adjusting:**
        *   If the spaceship is too jittery or unresponsive, increase the `hand_area_threshold` value.
        *   If the spaceship moves too much with small hand movements, decrease the `hand_area_threshold` value.
    *   **Experimentation:**  Start with a default value (e.g., 10000) and adjust it slightly until you find a comfortable setting.

3.  **Control the Spaceship:**

    *   **Hand Placement:** Position your hand in front of your webcam so it's clearly visible.  The game tracks the position of your hand.
    *   **Movement:** Move your hand to navigate the spaceship horizontally across the screen.  The spaceship will generally follow the movement of your hand. Experiment to find the optimal way to control your ship.
    *   **Firing:** Press the `Spacebar` key to fire a laser.  There is a brief cooldown period between laser shots to prevent rapid-fire.

4.  **Objective:**

    *   **Defeat the VC:** The VC is a special, more challenging enemy.  It is the primary target.
    *   **Avoid Other Enemies:**  While destroying regular enemies might be fun, it doesn't increase your score.  Focus on dodging them while targeting the VC.
    *   **Health & Score:**  Keep an eye on the health bar (representing the VC's health) and your score, both displayed on the screen.

5.  **Victory:**  The game ends in victory when you successfully destroy the VC (the VC's health reaches zero). A victory message will be displayed.

6.  **Exiting the Game:**  To quit the game, click the close button on the game window or press the `X` key.

## License

This project is licensed under the MIT License.  See the `LICENSE` file for details.

## Acknowledgements

This game was developed using the following fantastic libraries:

*   **Pygame:** A cross-platform set of Python modules designed for creating games.  [https://www.pygame.org/](https://www.pygame.org/)
*   **NumPy:** A powerful library for scientific computing and array manipulation. [https://numpy.org/](https://numpy.org/)
*   **OpenCV (cv2):** A library for computer vision tasks, including image and video processing. [https://opencv.org/](https://opencv.org/)
*   **MediaPipe:** A framework for building multimodal (e.g., video, audio) applied ML pipelines. [https://developers.google.com/mediapipe](https://developers.google.com/mediapipe)

## Author

This game was developed by [iman, Blackboyzeus, Potus] as part of the SensoryLink/Project Thalamus project.

## Contributing

Enjoy playing Kill the VC!  We welcome contributions.  Please feel free to submit bug reports, feature requests, or pull requests through the project's issue tracker or repository (if available).

Have fun defeating the VC!
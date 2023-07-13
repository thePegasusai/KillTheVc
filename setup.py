import sys
from cx_Freeze import setup, Executable

# Include additional modules if required
additional_modules = []

# Dependencies are automatically detected, but it might need fine-tuning
build_exe_options = {
    "packages": [],
    "includes": additional_modules,
    "include_files": []
}

# Create an executable for the splash.py script
splash_executable = Executable(
    script="splash.py",
    base=None,
    targetName="splash.exe"  # Change the targetName if desired
)

# Create an executable for the game.py script
game_executable = Executable(
    script="game.py",
    base=None,
    targetName="game.exe"  # Change the targetName if desired
)

# Add both executables to the executables list
executables = [splash_executable, game_executable]

# Setup cx_Freeze
setup(
    name="My Game",
    version="1.0",
    description="My Game Description",
    options={"build_exe": build_exe_options},
    executables=executables
)

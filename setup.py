from setuptools import setup, find_packages

setup(
    name="kill_the_vc",
    version="1.0.0",
    description="A hand gesture controlled space shooter game",
    author="iman, Blackboyzeus, Potus",
    author_email="example@example.com",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.1.0",
        "numpy>=1.20.0",
        "opencv-python>=4.5.0",
        "mediapipe>=0.8.9",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Games/Entertainment :: Arcade",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "kill-the-vc=game:main",
        ],
    },
)

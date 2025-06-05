#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/python/venv/bin/activate"
cd "$DIR/game"
python game.py

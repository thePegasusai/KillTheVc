#!/bin/bash
# Fix Python paths for macOS bundled applications

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$SCRIPT_DIR"

# Check if we're in a bundled app
if [[ "$SCRIPT_DIR" == *"Resources/app"* ]]; then
    # Extract the app path
    APP_DIR=$(echo "$SCRIPT_DIR" | sed 's/\/Contents\/Resources\/app.*//')
    echo "Detected bundled app at: $APP_DIR"
else
    echo "Not running in a bundled app, using script directory: $APP_DIR"
fi

# Find the Python binary
PYTHON_BIN="$APP_DIR/Contents/Resources/app/python/venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    echo "Python binary not found at: $PYTHON_BIN"
    exit 1
fi

echo "Found Python binary at: $PYTHON_BIN"

# Use otool to find the library dependencies
OTOOL_OUTPUT=$(otool -L "$PYTHON_BIN")
echo "otool output:"
echo "$OTOOL_OUTPUT"

# Extract the Python library reference
PYTHON_LIB=$(echo "$OTOOL_OUTPUT" | grep -E 'Python3|libpython3' | head -1 | awk '{print $1}')
if [ -z "$PYTHON_LIB" ]; then
    echo "Could not find Python library reference in otool output"
    exit 1
fi

echo "Python library reference: $PYTHON_LIB"

# Extract the library filename
LIB_FILENAME=$(basename "$PYTHON_LIB")
echo "Library filename: $LIB_FILENAME"

# Find the actual library file on the system
SYSTEM_LIB_PATH=""
POSSIBLE_PATHS=(
    "/usr/local/Frameworks/$LIB_FILENAME"
    "/Library/Frameworks/$LIB_FILENAME"
    "/usr/lib/$LIB_FILENAME"
    "/usr/local/lib/$LIB_FILENAME"
    "/opt/homebrew/lib/$LIB_FILENAME"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        SYSTEM_LIB_PATH="$path"
        break
    fi
done

if [ -z "$SYSTEM_LIB_PATH" ]; then
    # Try to find it using mdfind
    MDFIND_OUTPUT=$(mdfind -name "$LIB_FILENAME" | head -1)
    if [ -n "$MDFIND_OUTPUT" ] && [ -f "$MDFIND_OUTPUT" ]; then
        SYSTEM_LIB_PATH="$MDFIND_OUTPUT"
    fi
fi

if [ -z "$SYSTEM_LIB_PATH" ]; then
    echo "Could not find Python library on the system"
    exit 1
fi

echo "System library path: $SYSTEM_LIB_PATH"

# Create the target directory if it doesn't exist
TARGET_DIR="$(dirname "$PYTHON_BIN")"
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
fi

# Create a symbolic link to the system library
LINK_PATH="$APP_DIR/Contents/Resources/app/python/venv/$LIB_FILENAME"
echo "Creating symbolic link: $LINK_PATH -> $SYSTEM_LIB_PATH"

# Remove existing link if it exists
if [ -L "$LINK_PATH" ] || [ -f "$LINK_PATH" ]; then
    rm "$LINK_PATH"
fi

# Create the symbolic link
ln -s "$SYSTEM_LIB_PATH" "$LINK_PATH"

echo "Python path fix completed successfully"
exit 0

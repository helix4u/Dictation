#!/bin/bash

echo "Whisper Dictation - Installation and Startup Script"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ from your package manager or https://python.org"
    exit 1
fi

echo "Python found. Checking version..."
python3 -c "import sys; print(f'Python {sys.version}')"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install PyTorch with CUDA support first
echo "Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to install CUDA-enabled PyTorch"
    echo "Falling back to CPU-only PyTorch..."
    pip install torch torchvision torchaudio
fi

# Install other requirements
echo "Installing other dependencies from requirements.txt..."
pip install -r requirements.txt --no-deps
pip install pyaudio pyautogui keyboard numpy simpleaudio pyperclip scipy openai-whisper
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo ""
    echo "Common issues:"
    echo "- PyAudio may require system audio libraries"
    echo "- On Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio"
    echo "- On macOS: brew install portaudio"
    echo "- On CentOS/RHEL: sudo yum install portaudio-devel"
    echo "- CUDA drivers may need to be updated for GPU acceleration"
    echo ""
    echo "For keyboard permissions on macOS:"
    echo "System Preferences > Security & Privacy > Privacy > Accessibility"
    echo "Add Terminal or your Python interpreter to the list"
    exit 1
fi

echo ""
echo "Installation completed successfully!"
echo ""
echo "Starting Whisper Dictation..."
echo "Press Ctrl+Alt+Space to start/stop recording"
echo "Press Shift+Esc to quit"
echo ""

# Start the dictation script
python dictation.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "Script ended with an error."
    read -p "Press Enter to close..."
fi

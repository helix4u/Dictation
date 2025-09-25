@echo off
echo Whisper Dictation - Installation and Startup Script
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; print(f'Python {sys.version}')"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch with CUDA support first
echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 (
    echo WARNING: Failed to install CUDA-enabled PyTorch
    echo Falling back to CPU-only PyTorch...
    pip install torch torchvision torchaudio
)

REM Install other requirements
echo Installing other dependencies from requirements.txt...
pip install -r requirements.txt --no-deps
pip install pyaudio pyautogui keyboard numpy simpleaudio pyperclip scipy openai-whisper
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Common issues:
    echo - PyAudio may require Microsoft Visual C++ Build Tools
    echo - Try: pip install --only-binary=all pyaudio
    echo - Or install from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo - CUDA drivers may need to be updated for GPU acceleration
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo Starting Whisper Dictation...
echo Press Ctrl+Alt+Space to start/stop recording
echo Press Shift+Esc to quit
echo.

REM Start the dictation script
python dictation.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Script ended with an error. Press any key to close.
    pause >nul
)

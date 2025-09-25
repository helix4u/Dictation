# Whisper Dictation

Whisper Dictation is a hotkey-driven desktop dictation tool that records short bursts of audio, transcribes them with OpenAI Whisper, and types the recognized text into whichever application currently has focus.

## Features
- Quick toggle (Ctrl+Alt+Space) to record speech and insert the transcription in place
- Automatic Whisper model loading/unloading to conserve GPU memory when idle
- Device selection prompt so you pick the correct microphone at startup
- Audible start/stop beeps to confirm recording state
- Logging of every recording session to `recording_log.txt`

## Prerequisites
- Python 3.9 or newer
- PortAudio runtime (needed by PyAudio). On Windows install the PyAudio wheels, on macOS use `brew install portaudio`, on Linux use your package manager.

## Installation

### Quick Start (Recommended)
Simply run the appropriate script for your operating system:

**Windows:**
```cmd
start.bat
```

**macOS/Linux:**
```bash
./start.sh
```

These scripts will automatically:
- Check for Python 3.9+ installation
- Create a virtual environment
- Install all required dependencies
- Start the dictation application

### Manual Installation
If you prefer to install manually:

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install openai-whisper torch pyaudio pyautogui keyboard numpy simpleaudio pyperclip
   ```

3. Optional: place any Whisper GGML models inside the `models/` directory for future experiments. The current Python workflow downloads models automatically through the `whisper` package.

### GPU Acceleration
The installation scripts automatically install CUDA-enabled PyTorch for GPU acceleration. If CUDA installation fails, the scripts will fall back to CPU-only PyTorch.

**Requirements for GPU acceleration:**
- NVIDIA GPU with CUDA support
- CUDA 11.8+ drivers installed
- Compatible PyTorch version (automatically installed)

If you need a different CUDA version, visit [pytorch.org](https://pytorch.org/get-started/locally/) for your specific setup.

## Usage

### Starting the Application
**Option 1 - Using the installation scripts (recommended):**
```bash
# Windows
start.bat

# macOS/Linux
./start.sh
```

**Option 2 - Manual start:**
```bash
python dictation.py
```

### Using the Dictation Tool
1. Choose the input device index when prompted. The script lists every available capture device that exposes input channels.
2. Press `Ctrl+Alt+Space` to begin a recording. A high-pitched beep confirms recording has started.
3. Press the hotkey again to stop. A lower beep plays, the audio is transcribed with the Whisper `tiny.en` model, and the resulting text is typed into the active window.
4. Repeat as needed. Press `Shift+Esc` to quit the script entirely.

While the script is idle for more than 15 seconds, the Whisper model is automatically unloaded and GPU memory reclaimed. The next recording triggers a reload.

## Customisation
- **Model size**: change the argument to `whisper.load_model()` in `dictation.py` to use larger or multilingual models (requires more VRAM/CPU).
- **Hotkey**: adjust the binding in the `keyboard.add_hotkey()` call.
- **Beep tones**: update the frequency values in `play_beep()` if you prefer different confirmation sounds.
- **Filtering**: tweak the string cleanup logic in `process_audio()` if you want to block specific words or punctuation.

## Logging
Session events (start/stop timestamps) are appended to `recording_log.txt`. Keep the file around for auditing, or rotate it manually if it grows too large.

## Project Structure
- `dictation.py` – main dictation workflow that captures audio, transcribes with Whisper, and simulates keyboard entry.
- `start.bat` – Windows installation and startup script.
- `start.sh` – Unix/Linux/macOS installation and startup script.
- `requirements.txt` – Python dependencies list for easy installation.
- `models/` – local store for quantised Whisper models (not used directly by the Python script yet).
- `recorded_audio.wav` – sample recording for testing.
- `recording_log.txt` – rolling log file written by the dictation script.

## Troubleshooting

### Installation Issues
- **PyAudio installation fails**: 
  - Windows: Install Microsoft Visual C++ Build Tools or try `pip install --only-binary=all pyaudio`
  - macOS: `brew install portaudio` then retry
  - Linux: `sudo apt-get install portaudio19-dev python3-pyaudio` (Ubuntu/Debian) or equivalent for your distro
- **Permission denied on start.sh**: Run `chmod +x start.sh` to make the script executable
- **Python not found**: Ensure Python 3.9+ is installed and in your system PATH

### Runtime Issues
- **No text appears**: confirm the target window accepts keyboard input and that accessibility permissions are granted (macOS requires enabling accessibility for the terminal/Python process).
- **Hotkey not firing**: some virtual desktops intercept complex hotkeys; change the key combo in `dictation.py` if needed.
- **Audio glitches**: lower the buffer size or sample rate in `record_audio()` or verify the microphone is not used by other apps.
- **CUDA out of memory**: edit `whisper.load_model()` to use a smaller model or rely on CPU inference.

## Roadmap Ideas
- Persistent settings file for input device selection and hotkeys
- Live streaming transcription instead of post-stop processing
- UI overlay showing recording status and last transcript
- Integration with the local GGML models stored in `models/`
  
## Support

If the tool is helpful, consider supporting it on [Ko-fi](https://ko-fi.com/gille).

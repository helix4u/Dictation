# Whisper Dictation

Whisper Dictation is a hotkey-driven desktop dictation tool that records short bursts of audio, transcribes them with OpenAI Whisper, and types the recognized text into whichever application currently has focus. The repository also bundles an experimental "shadow play" style recorder that can preserve the previous minute of screen and microphone activity on demand.

## Features
- Quick toggle (Ctrl+Alt+Space) to record speech and insert the transcription in place
- Automatic Whisper model loading/unloading to conserve GPU memory when idle
- Device selection prompt so you pick the correct microphone at startup
- Audible start/stop beeps to confirm recording state
- Logging of every recording session to `recording_log.txt`
- Optional screen/audio buffer capture script (`shadowplaydesktop.py`) for retroactive recording

## Prerequisites
- Python 3.9 or newer
- FFmpeg command-line tools on your PATH (required for `shadowplaydesktop.py`)
- PortAudio runtime (needed by PyAudio). On Windows install the PyAudio wheels, on macOS use `brew install portaudio`, on Linux use your package manager.

## Installation
1. Create and activate a virtual environment (recommended).
2. Install Python dependencies:
   ```bash
   pip install openai-whisper torch pyaudio pyautogui keyboard numpy simpleaudio ffmpeg-python
   ```
   - GPU acceleration: install the CUDA-enabled build of PyTorch that matches your drivers (see [pytorch.org](https://pytorch.org/get-started/locally/)).
   - macOS/Linux users may need additional permissions for global hotkeys (the `keyboard` package).
3. Optional: place any Whisper GGML models inside the `models/` directory for future experiments. The current Python workflow downloads models automatically through the `whisper` package.

## Usage
1. Start the dictation agent:
   ```bash
   python dictation.py
   ```
2. Choose the input device index when prompted. The script lists every available capture device that exposes input channels.
3. Press `Ctrl+Alt+Space` to begin a recording. A high-pitched beep confirms recording has started.
4. Press the hotkey again to stop. A lower beep plays, the audio is transcribed with the Whisper `tiny.en` model, and the resulting text is typed into the active window.
5. Repeat as needed. Press `Shift+Esc` to quit the script entirely.

While the script is idle for more than 15 seconds, the Whisper model is automatically unloaded and GPU memory reclaimed. The next recording triggers a reload.

## Customisation
- **Model size**: change the argument to `whisper.load_model()` in `dictation.py` to use larger or multilingual models (requires more VRAM/CPU).
- **Hotkey**: adjust the binding in the `keyboard.add_hotkey()` call.
- **Beep tones**: update the frequency values in `play_beep()` if you prefer different confirmation sounds.
- **Filtering**: tweak the string cleanup logic in `process_audio()` if you want to block specific words or punctuation.

## Logging
Session events (start/stop timestamps) are appended to `recording_log.txt`. Keep the file around for auditing, or rotate it manually if it grows too large.

## Additional Tools
`shadowplaydesktop.py` offers a rolling one-minute buffer of screen captures and microphone audio. Run it separately from dictation when you need a manual "save last minute" feature:
```bash
python shadowplaydesktop.py
```
- Press `Ctrl+Shift+S` to write the buffered video (`output_video.mp4`) and audio (`output_audio.wav`) to disk.
- Press `Esc` to stop the recorder.

This script depends heavily on FFmpeg (`ffmpeg-python`) and may require tuning to match your monitor resolution and performance budget.

## Project Structure
- `dictation.py` – main dictation workflow that captures audio, transcribes with Whisper, and simulates keyboard entry.
- `shadowplaydesktop.py` – experimental retroactive recorder for screen+audio.
- `models/` – local store for quantised Whisper models (not used directly by the Python script yet).
- `recorded_audio.wav` – sample recording for testing.
- `recording_log.txt` – rolling log file written by the dictation script.
- `SILENCE_DURATION` – placeholder file kept for backwards compatibility.

## Troubleshooting
- **No text appears**: confirm the target window accepts keyboard input and that accessibility permissions are granted (macOS requires enabling accessibility for the terminal/Python process).
- **Hotkey not firing**: some virtual desktops intercept complex hotkeys; change the key combo in `dictation.py` if needed.
- **Audio glitches**: lower the buffer size or sample rate in `record_audio()` or verify the microphone is not used by other apps.
- **CUDA out of memory**: edit `whisper.load_model()` to use a smaller model or rely on CPU inference.

## Roadmap Ideas
- Persistent settings file for input device selection and hotkeys
- Live streaming transcription instead of post-stop processing
- UI overlay showing recording status and last transcript
- Integration with the local GGML models stored in `models/`

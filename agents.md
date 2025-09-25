# Dictation Agent

This project focuses on a single lightweight agent that handles real-time dictation tasks. The Python script coordinates through threads, queues, and global flags rather than a formal agent framework, but the behavior maps cleanly to discrete responsibilities.

## Dictation Agent (`dictation.py`)

### Responsibilities
- Monitor the global hotkey (`Ctrl+Alt+Space`) and toggle speech capture.
- Stream raw microphone frames into a shared queue while the user is recording.
- Transcribe accumulated audio with Whisper once recording stops and emit the transcript via simulated keyboard input.
- Manage Whisper model lifecycle, loading it on demand and unloading it after 15 seconds of inactivity to free GPU memory.
- Log each recording session to `recording_log.txt` and play audible cues for state changes.

### Key Components
- **Hotkey Controller**: `keyboard.add_hotkey()` binds `toggle_recording()`, which flips the `recording` flag, starts/stops audio capture threads, and orchestrates beeps/logging.
- **Recorder Worker**: `record_audio()` runs on its own thread, pushing 16 kHz mono frames into `audio_queue` while `recording` remains `True`.
- **Transcription Worker**: `process_audio()` drains `audio_queue`, normalises the waveform, calls `model.transcribe()`, filters the output, and types the result with `pyautogui.write()`.
- **Model Lifecycle Monitor**: `monitor_model_usage()` runs as a daemon thread, tracking `last_model_use_time` and calling `unload_model()` after a 15-second idle window.

### Runtime Flow
1. Script start: user selects an audio device; the monitor thread starts immediately.
2. Hotkey pressed: `toggle_recording()` marks `recording=True`, plays a high beep, and spawns `record_audio()`.
3. Hotkey pressed again: recording stops, a low beep plays, audio is transcribed, text is injected into the active window, and usage timestamps update.
4. Idle: after 15 seconds without transcription, `monitor_model_usage()` frees GPU VRAM.
5. Exit: `keyboard.wait('shift+esc')` keeps the agent alive until the user quits.

## Technical Considerations
- **Hotkeys**: The agent relies on system-wide hooks (`keyboard` module). It may need additional privileges or accessibility permissions depending on the OS.
- **Resource Cleanup**: Audio workers release system resources when their control flags flip; ensure hotkeys always toggle the corresponding state to avoid dangling streams.
- **Thread Safety**: Global queues/flags are intentionally simple; if you extend the project, replace them with higher-level primitives (Events, Futures) to prevent race conditions.

## Extensibility Ideas
- Introduce a supervisor script that can start/stop the agent and expose status via a tray icon or web API.
- Convert the transcription step into a streaming agent that feeds partial hypotheses to the UI in real time.
- Allow `dictation.py` to switch between Python Whisper and local GGML binaries stored in `models/`.
- Persist preferences (device index, hotkeys, model choice) in a config file so the agent loads consistent settings.

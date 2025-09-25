import pyaudio
import whisper
import pyautogui
import keyboard
import threading
import queue
import time
import numpy as np
import logging
import simpleaudio as sa  # Cross-platform sound playback
import torch
import gc
import sys
import contextlib

try:
    import pyperclip
except ImportError:
    pyperclip = None

PASTE_COMBO = 'command+v' if sys.platform == 'darwin' else 'ctrl+v'

# Initialize Whisper model placeholder
model = None

# Queue for audio frames
audio_queue = queue.Queue()

def emit_transcript(text: str) -> None:
    """Emit text via a single paste operation when possible for faster output."""
    if not text:
        return

    for key in ('ctrl', 'alt', 'shift'):
        pyautogui.keyUp(key)

    if pyperclip:
        previous = None
        try:
            previous = pyperclip.paste()
        except Exception:
            previous = None
        try:
            pyperclip.copy(text)
            time.sleep(0.02)
            keyboard.send(PASTE_COMBO)
            time.sleep(0.05)
        except Exception:
            keyboard.write(text, delay=0)
            return
        if previous is not None:
            with contextlib.suppress(Exception):
                pyperclip.copy(previous)
    else:
        keyboard.write(text, delay=0)
# Setup logging
logging.basicConfig(filename='recording_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to list and select an audio input device
def select_audio_input_device():
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print("Available audio input devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"{i}: {device_info['name']}")
    
    # Adjust the default for your use case.
    device_index = int(input("Select the device index for audio input (default is 1): ") or 1)
    p.terminate()
    return device_index

# Function to load the Whisper model if not already loaded
def load_model():
    global model
    if model is None:
        print("Loading Whisper model...")
        model = whisper.load_model("tiny.en")
        print("Model loaded.")
    # Update the last used timestamp
    global last_model_use_time
    last_model_use_time = time.time()

# Function to unload the Whisper model from VRAM
def unload_model():
    global model
    if model is not None:
        print("Unloading Whisper model from VRAM...")
        del model
        model = None
        torch.cuda.empty_cache()
        gc.collect()
        print("Model unloaded.")
    print("Press ctrl+alt+space to start/stop recording and process dictation.")

# Function to monitor model usage and unload if not used for 15 seconds
def monitor_model_usage():
    while True:
        if model is not None and time.time() - last_model_use_time > 15:
            unload_model()
        time.sleep(1)

# Function to record audio from selected input device
def record_audio(device_index):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=device_index, frames_per_buffer=1024)

    while recording:
        data = stream.read(1024)
        audio_queue.put(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to process audio and do real-time dictation
def process_audio():
    load_model()  # Load the model when starting to process audio
    audio_frames = []
    while not audio_queue.empty():
        data = audio_queue.get()
        audio_frames.append(data)

    if audio_frames:
        audio_data = np.frombuffer(b''.join(audio_frames), dtype=np.int16)
        audio_data = audio_data.astype(np.float32) / 32768.0
        text = model.transcribe(audio_data)["text"]

        # Filter out unwanted phrases
        filtered_text = text.replace("", "").strip()

        # Additional filters for whitespace or specific unwanted text
        if filtered_text and filtered_text != "you" and filtered_text.strip():
            emit_transcript(filtered_text)
        time.sleep(0.5)

    print("Press ctrl+alt+space to start/stop recording and process dictation.")

# Function to generate and play a beep sound with customizable frequency
def play_beep(frequency=440, duration=0.1):
    fs = 44100  # Sampling rate
    t = np.linspace(0, duration, int(fs * duration), False)
    wave = np.sin(frequency * t * 2 * np.pi)
    audio = wave * (2**15 - 1) / np.max(np.abs(wave))
    audio = audio.astype(np.int16)
    play_obj = sa.play_buffer(audio, 1, 2, fs)
    play_obj.wait_done()

# Function to toggle recording
def toggle_recording():
    global recording
    if recording:
        recording = False  # Stop recording
        print("Recording stopped.")
        logging.info("Recording stopped.")
        play_beep(frequency=400)  # Change this if desired.. e.g. Play lower-pitched beep sound on stop (330 is perfect fourth below 440 Hz)
        process_audio()  # Process audio after recording stops
    else:
        recording = True  # Start recording
        print("Recording started...")
        logging.info("Recording started.")
        play_beep(frequency=440)  # Play higher-pitched beep sound on start
        threading.Thread(target=record_audio, args=(selected_device_index,)).start()

    print("Press ctrl+alt+space to start/stop recording and process dictation.")

# Select audio input device
selected_device_index = select_audio_input_device()

# Setup hotkey
recording = False
keyboard.add_hotkey('ctrl+alt+space', toggle_recording)

# Start the model usage monitor thread
last_model_use_time = time.time()
model_monitor_thread = threading.Thread(target=monitor_model_usage, daemon=True)
model_monitor_thread.start()

print("Press ctrl+alt+space to start/stop recording and process dictation.")
keyboard.wait('shift+esc')  # Press 'Esc' to exit the script






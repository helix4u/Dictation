import simpler_whisper
import numpy as np
import pyaudio
import pyautogui
import keyboard
import threading
import queue
import time
import logging
import simpleaudio as sa  # For sound playback
import gc
import os

# Queue for audio frames
audio_queue = queue.Queue()

# Setup logging
logging.basicConfig(filename='recording_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Default directory and model path setup (sure, AI, why not...)
default_dir = "F:\\AITools\\WhisperDictationProj" # Update with your specific model dir
model_subdir = os.path.join(default_dir, "models") 
model_path = os.path.join(model_subdir, "ggml-model-whisper-small-q5_1.bin")  # Update with your specific model filename

# Load the Whisper model
model = simpler_whisper.WhisperModel(model_path, use_gpu=True)

# Function to list and select an audio input device
def select_audio_input_device():
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print("Available audio input devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"{i}: {device_info['name']}")
    
    device_index = int(input("Select the device index for audio input (default is 1): ") or 1)
    p.terminate()
    return device_index

# Function to unload unused resources
def unload_resources():
    global model
    if model:
        print("Unloading resources...")
        model = None
        gc.collect()
        print("Resources unloaded.")

# Function to record audio from the selected input device
def record_audio(device_index):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=device_index, frames_per_buffer=1024)

    while recording:
        data = stream.read(1024)
        audio_queue.put(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to process audio and transcribe using simpler_whisper
def process_audio():
    audio_frames = []
    while not audio_queue.empty():
        data = audio_queue.get()
        audio_frames.append(data)

    if audio_frames:
        # Convert audio frames to a single array
        audio_data = np.frombuffer(b''.join(audio_frames), dtype=np.int16).astype(np.float32) / 32768.0

        # Transcribe audio using simpler_whisper
        result = model.transcribe(audio_data)
        output_text = ""
        for segment in result:
            text = segment.text.strip()
            if text:
                # Always add a space after the text segment
                output_text += text + " "

        # Type the complete text at once
        if output_text:
            pyautogui.keyUp('ctrl')
            pyautogui.keyUp('alt')
            pyautogui.keyUp('shift')
            pyautogui.write(output_text.strip())  # Remove trailing space before typing

        print("Transcription completed.")

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
        play_beep(frequency=330)  # Lower-pitched beep on stop
        process_audio()  # Process audio after recording stops
    else:
        recording = True  # Start recording
        print("Recording started...")
        logging.info("Recording started.")
        play_beep(frequency=440)  # Higher-pitched beep on start
        threading.Thread(target=record_audio, args=(selected_device_index,)).start()

# Select audio input device
selected_device_index = select_audio_input_device()

# Setup hotkey
recording = False
keyboard.add_hotkey('ctrl+alt+space', toggle_recording)

print("Press ctrl+alt+space to start/stop recording and process dictation.")
keyboard.wait('ctrl+shift+q')  # Press 'Ctrl+Shift+Q' to exit the script

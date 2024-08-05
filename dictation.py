import pyaudio
import whisper
import pyautogui
import keyboard
import threading
import queue
import time
import numpy as np

# Initialize Whisper model
model = whisper.load_model("small")

# Queue for audio frames
audio_queue = queue.Queue()

# Function to list and select an audio input device
def select_audio_input_device():
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print("Available audio input devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"{i}: {device_info['name']}")
    
    device_index = int(input("Select the device index for audio input (default is 6): ") or 6)
    p.terminate()
    return device_index

# Function to record audio from selected input device
def record_audio(device_index):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=device_index, frames_per_buffer=512)

    while recording:
        data = stream.read(4096)
        audio_queue.put(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to process audio and do real-time dictation
def process_audio():
    audio_frames = []
    while not audio_queue.empty():
        data = audio_queue.get()
        audio_frames.append(data)

    if audio_frames:
        audio_data = np.frombuffer(b''.join(audio_frames), dtype=np.int16)
        audio_data = audio_data.astype(np.float32) / 32768.0
        text = model.transcribe(audio_data)["text"]

        # Filter out unwanted phrases
        filtered_text = text.replace("Thank you.", "").strip()

        # Additional filters for whitespace or specific unwanted text
        if filtered_text and filtered_text != "you" and filtered_text.strip():
            pyautogui.write(filtered_text)
        time.sleep(0.5)

# Function to toggle recording
def toggle_recording():
    global recording
    if recording:
        recording = False  # Stop recording
        process_audio()  # Process audio after recording stops
    else:
        recording = True  # Start recording
        threading.Thread(target=record_audio, args=(selected_device_index,)).start()

# Select audio input device
selected_device_index = select_audio_input_device()

# Setup hotkey
recording = False
keyboard.add_hotkey('ctrl+shift+alt+s', toggle_recording)

print("Press Ctrl+Shift+Alt+S to start/stop recording and process dictation.")
keyboard.wait('esc')  # Press 'Esc' to exit the script

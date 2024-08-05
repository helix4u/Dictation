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

# Parameters for silence detection
THRESHOLD = 200  # Adjust this based on your environment's noise level
SILENCE_DURATION = 2  # seconds of silence to consider it a delimiter

# Function to list and select an audio input device
def select_audio_input_device():
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print("Available audio input devices:")
    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"{i}: {device_info['name']}")
    
    device_index = int(input("Select the device index for audio input (default is 0): ") or 0)
    p.terminate()
    return device_index

# Function to record audio from selected input device
def record_audio(device_index):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=device_index, frames_per_buffer=1024)

    silence_start_time = None

    while True:
        if not recording:
            break
        data = stream.read(8096)
        audio_queue.put(data)

        # Check if the current audio chunk is silent
        audio_np = np.frombuffer(data, dtype=np.int16)
        if np.abs(audio_np).mean() < THRESHOLD:
            if silence_start_time is None:
                silence_start_time = time.time()
            elif time.time() - silence_start_time > SILENCE_DURATION:
                audio_queue.put(None)  # Insert a marker for silence
                silence_start_time = None
        else:
            silence_start_time = None

    stream.stop_stream()
    stream.close()
    p.terminate()

# Function to process audio and do real-time dictation
def process_audio():
    while True:
        if not recording and audio_queue.empty():
            break

        audio_frames = []
        while True:
            data = audio_queue.get()
            if data is None:
                break
            audio_frames.append(data)

        if audio_frames:
            audio_data = np.frombuffer(b''.join(audio_frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0
            text = model.transcribe(audio_data)["text"]

            # Filter out unwanted phrases
            filtered_text = text.replace("Thank you.", "").strip()

            if filtered_text:  # Only type if there's valid text
                pyautogui.write(filtered_text)
            time.sleep(0.5)

# Function to toggle recording
def toggle_recording():
    global recording
    if recording:
        recording = False
    else:
        recording = True
        threading.Thread(target=record_audio, args=(selected_device_index,)).start()
        threading.Thread(target=process_audio).start()

# Select audio input device
selected_device_index = select_audio_input_device()

# Setup hotkey
recording = False
keyboard.add_hotkey('ctrl+shift+alt+s', toggle_recording)

print("Press Ctrl+Shift+Alt+S to toggle dictation.")
keyboard.wait('esc')  # Press 'Esc' to exit the script

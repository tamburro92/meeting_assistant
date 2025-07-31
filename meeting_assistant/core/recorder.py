import os
import shutil
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import ffmpeg

SAMPLE_RATE = 44100
CHANNELS = 1
FILENAME = "recordings/meeting.wav"

recording = []
is_recording = False

def audio_callback(indata, frames, time_info, status):
    if is_recording:
        recording.append(indata.copy())

def get_input_devices():
    devices = sd.query_devices()
    input_devices = {device['name']: i for i, device in enumerate(devices) if device['max_input_channels'] > 0}
    print(input_devices)
    return input_devices

def start_recording(device_id=None):
    global is_recording, recording
    recording = []
    is_recording = True
    os.makedirs("recordings", exist_ok=True)
    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, device=device_id)
    stream.start()
    return stream

def stop_recording(stream):
    global is_recording
    is_recording = False
    stream.stop()
    audio_data = np.concatenate(recording, axis=0)
    write(FILENAME, SAMPLE_RATE, audio_data)
    return FILENAME

def use_existing_audio(filepath):
    os.makedirs("recordings", exist_ok=True)
    target = FILENAME
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".wav":
        shutil.copy(filepath, target)
    else:
        # Conversione automatica in wav con ffmpeg
        try:
            ffmpeg.input(filepath).output(target, ac=1, ar=SAMPLE_RATE).run(overwrite_output=True)
        except ffmpeg.Error as e:
            print("Errore durante la conversione:", e)
            raise RuntimeError("Errore nella conversione audio con ffmpeg.")

    return target

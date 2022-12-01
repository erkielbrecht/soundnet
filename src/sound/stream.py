import time
from collections.abc import Callable, Sized
from threading import Thread

import numpy as np
import sounddevice as sd

import config

# Getting the constants.
SPS = int(config.get("sound", "samplerate"))
CHANNELS = int(config.get("sound", "channels"))
R_VOLUME = config.get("sound", "r_volume")
ROUND = config.get("sound", "round")

# Function constants.
RUN = True
PLAYING = False
EMITTING = False
RECORDING = False
LISTENING = False


# Function for retrieving the current input hz.
def get_current_input_hz():
    if current_vol > R_VOLUME:
        return round(current_hz, ROUND)
    else:
        return 0


# Manually set HZ for testing.
def set_hz(x):
    global hz
    print("Manually setting the hz to play", x)
    hz = x


# Starting and stopping the audio stream.
def start_stream():
    t.start()


def end_stream():
    global RUN
    RUN = False


# Generates a sine wave for outdata.
def generate_sine(idx, frames, hz):
    wave = (idx + np.arange(frames)) / SPS
    wave = wave.reshape(-1, 1)
    return 0.2 * np.sin(2 * np.pi * hz * wave)


# Thread that contains the audio stream.
def stream_init() -> None:
    global hz, current_hz, latency
    start_idx = 0
    current_frame = 0

    # Callback function for the stream.
    def callback(indata, outdata, frames, time, status):
        nonlocal start_idx, current_frame
        global current_hz, current_vol, PLAYING, play_data

        if PLAYING:
            chunksize = min(len(play_data) - current_frame, frames)
            outdata[:chunksize] = play_data[current_frame:current_frame + chunksize]
            if chunksize < frames:
                outdata[:] = 0
                PLAYING = False
                current_frame = 0
                play_callback(None, None)
            current_frame += chunksize

        if EMITTING:
            outdata[:] = generate_sine(start_idx, frames, hz)

        if RECORDING:
            q.append([indata.copy(), frames])

        if LISTENING:
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=SPS))
            current_vol = np.max(magnitude)
            current_hz = np.argmax(magnitude)

        start_idx += frames

    # Defining the stream.
    stream = sd.Stream(
        samplerate=SPS,
        channels=CHANNELS,
        callback=callback,
        latency='high'
    )

    # Starting the stream
    with stream:
        print("Stream started")
        while RUN:
            time.sleep(1)


# Base variables.
hz = 0
current_hz = 0
current_vol = 0
play_data: Sized = []
play_callback: Callable = lambda *args: None

q = []
t = Thread(target=stream_init)

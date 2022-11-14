import sounddevice as sd
import numpy as np
import config as conf
from threading import Thread
import time

#Getting the constants.
SPS = int(conf.get("samplerate"))
CHANNELS = int(conf.get("channels"))
RUN = True
ROUND_INPUT = -1

#Funciton for retrieveing the current input hz.
def get_current_input_hz():
    return round(current_hz, ROUND_INPUT)

#Play an array with interval t (Normal python list)
def play_array(array, t):
    #Thread for playing the array
    def play_thread():
        global hz
        for i in array:
            hz = i
            time.sleep(t)
        hz = 0
    
    #Starting the playing thread
    x = Thread(target=play_thread)
    x.start()


#Manually set HZ for testing.
def set_hz(x):
    global hz
    print("Manually setting the hz to play", x)
    hz = x

#Starting and stopping the audio stream.
def start_stream():
    t.start()

def end_stream():
    global RUN
    RUN = False

#Generates a sine wave for outdata.
def generate_sine(idx, frames, hz):
    wave = (idx + np.arange(frames)) / SPS
    wave = wave.reshape(-1, 1)
    return 0.2 * np.sin(2 * np.pi * hz * wave)


#Thread that contains the audio stream.
def stream() -> None:
    global hz, current_hz
    start_idx = 0

    #Callback function for the stream.
    def callback(indata, outdata, frames, time, status):
        nonlocal start_idx
        global current_hz

        outdata[:] = generate_sine(start_idx, frames, hz)

        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=SPS))
        current_hz = np.argmax(magnitude)

        start_idx += frames

    #Defining the stream.
    stream = sd.Stream(
        samplerate=SPS,
        channels=CHANNELS, 
        callback=callback)

    #Starting the stream
    with stream:
        print("Stream started")
        while RUN: time.sleep(1)

#Base variables.      
hz = 0
current_hz = 0
t = Thread(target=stream)

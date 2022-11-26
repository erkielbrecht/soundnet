import sounddevice as sd
import numpy as np
import config as conf
from threading import Thread
import time

#Getting the constants.
SPS = int(conf.get("sound","samplerate"))
CHANNELS = int(conf.get("sound","channels"))
R_VOLUME = conf.get("sound","r_volume")
RUN = True

# Function for retrieveing the current input hz.
def get_current_input_hz():
    if rec_vol > R_VOLUME:
        return current_hz
    else:
        return 0

# Play the data
def emit_data(c_tone, h_tone, t_tone, header, data, t, t_c):
    # Thread for playing the array
    print(t)
    def play_thread():
        global hz
        hz=c_tone
        print("playing_ctone")
        time.sleep(t_c)
        hz=t_tone
        time.sleep(t_c)
        for i in header:
            hz = i
            time.sleep(t)
        hz=h_tone
        time.sleep(t_c)
        for i in data:
            hz = i
            time.sleep(t)
        hz=c_tone
        time.sleep(t_c)
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
        global current_hz, rec_vol

        outdata[:] = generate_sine(start_idx, frames, hz)

        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=SPS))
        rec_vol = np.max(magnitude)
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
rec_vol = 0
t = Thread(target=stream)   

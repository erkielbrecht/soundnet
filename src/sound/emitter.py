import numpy as np
import sounddevice as sd
import time

# Samples per second
sps = 44100

# Frequency / pitch
freq_hz = 440.0
freq_hz2 = 330.0
hz_list = [0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850]


start_idx = 0
hz_idx = 0

def callback(outdata, frames, time, status):
        if status:
            print(status)
        global start_idx, freq_hz, hz_idx
        
        if start_idx >= 1500 and hz_idx<60:
            start_idx = 0
            hz_idx+=1
        freq_hz = hz_list[hz_idx]*20
        t = (start_idx + np.arange(frames)) / sps
        t = t.reshape(-1, 1)
        outdata[:] = 0.2 * np.sin(2 * np.pi * freq_hz * t)
        start_idx += frames
        print(time)


# Play the waveform out the speakers
with sd.OutputStream(device=1,channels=1, callback=callback,samplerate=sps):
    print("Enter to quit")
    input()
    
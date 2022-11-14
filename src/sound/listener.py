import sounddevice as sd
import numpy as np

hz = 0
#hz_buffer = np.array([0,0,0])
#buffer_iter = 0

def callback(indata, outdata, frames, time, status):
    global hz#, buffer_iter, hz_buffer

    if status:
        print(status)
    

    magnitude = np.abs(np.fft.rfft(indata[:, 0], n=44100))
    current_hz = np.argmax(magnitude)
    #buffer_avg = np.mean(hz_buffer)

    #if buffer_iter > 2:
    #    buffer_iter = 0

    #if abs(current_hz - buffer_avg)<20:
    #    hz_buffer[buffer_iter] = current_hz
    #else:
    #    buffer_iter = 0
    #    hz_buffer[buffer_iter] = current_hz
    #    hz_buffer[1] = current_hz
    #    hz_buffer[2] = current_hz
    #buffer_iter+=1

    if np.max(magnitude) > 50 and abs(current_hz-hz) > 30:
        hz_new = round(current_hz, -1)
        if abs(hz_new - hz) > 10:
            hz = hz_new
            print(hz)





with sd.Stream(
            samplerate=44100,
            channels=1, 
            callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
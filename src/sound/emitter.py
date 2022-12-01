import config
import dict.dictionary as dict
import sound.stream as stream
from threading import Thread
import time
import numpy as np

LIVE = False

def emit(type, header, data):
    # Get the type tone corrseponding to a protocol.
    type_tone = config.get(type, 'type_tone')

    # Constants.
    SPS = config.get("sound", "samplerate")
    confirm_tone = int(config.get("sound", "confirm_tone"))
    header_tone = int(config.get("sound", "header_tone"))
    tone_speed = config.get("sound", "tone_speed")
    confirm_speed = config.get("sound", "confirm_speed")

    # Convert data to frequencies.
    data = dict.txt_to_freq(data)
    header = dict.txt_to_freq(header)

    # Construct the data before playing
    def construct_data():
        emit_data = (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * confirm_tone / SPS))
        emit_data = np.concatenate((emit_data, (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * type_tone / SPS))))
        for i in header:
            emit_data = np.concatenate((emit_data, (np.sin(2 * np.pi * np.arange(tone_speed * SPS).reshape(-1, 1) * i / SPS))))
        emit_data = np.concatenate(
            (emit_data, (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * header_tone / SPS))))
        for i in data:
            emit_data = np.concatenate((emit_data, (np.sin(2 * np.pi * np.arange(tone_speed * SPS).reshape(-1, 1) * i / SPS))))
        emit_data = np.concatenate(
            (emit_data, (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * confirm_tone / SPS))))
        return emit_data



    # Play the data
    def play_thread():
        # Enable emitting on stream
        stream.EMITTING = True
        stream.hz = confirm_tone
        time.sleep(confirm_speed)
        stream.hz = type_tone
        time.sleep(confirm_speed)
        for i in header:
            stream.hz = i
            time.sleep(tone_speed)
        stream.hz = header_tone
        time.sleep(confirm_tone)
        for i in data:
            stream.hz = i
            time.sleep(tone_speed)
        stream.hz = confirm_tone
        time.sleep(confirm_speed)
        stream.hz = 0
        # Disable emitting on stream
        stream.EMITTING = False

    # Starting the playing thread
    if LIVE:
        x = Thread(target=play_thread)
        x.start()
    else:
        emit_data = construct_data()
        stream.play_data = emit_data
        stream.PLAYING = True


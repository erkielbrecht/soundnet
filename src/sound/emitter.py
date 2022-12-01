import time
from collections.abc import Callable
from threading import Thread

import numpy as np

import config
import dict.dictionary as dict
import sound.stream as stream


def emit(callback_func: Callable, type: str, header: str, data: str, LIVE: bool = False,
         status_callback: Callable = None):
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

    def callback(status):
        if status_callback:
            status_callback(status)

    # Construct the data before playing
    def construct_data():
        callback("Constructing data for emitting.")
        emit_data = (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * confirm_tone / SPS))
        emit_data = np.concatenate(
            (emit_data, (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * type_tone / SPS))))
        for i in header:
            emit_data = np.concatenate(
                (emit_data, (np.sin(2 * np.pi * np.arange(tone_speed * SPS).reshape(-1, 1) * i / SPS))))
        emit_data = np.concatenate(
            (emit_data, (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * header_tone / SPS))))
        for i in data:
            emit_data = np.concatenate(
                (emit_data, (np.sin(2 * np.pi * np.arange(tone_speed * SPS).reshape(-1, 1) * i / SPS))))
        emit_data = np.concatenate(
            (emit_data, (np.sin(2 * np.pi * np.arange(confirm_speed * SPS).reshape(-1, 1) * confirm_tone / SPS))))
        return emit_data

    # Play the data
    def play_thread():
        # Enable emitting on stream
        callback("Emitting confirm tone.")
        stream.EMITTING = True
        stream.hz = confirm_tone
        time.sleep(confirm_speed)
        callback("Emitting type tone.")
        stream.hz = type_tone
        time.sleep(confirm_speed)
        callback("Emitting header.")
        for i in header:
            stream.hz = i
            time.sleep(tone_speed)
        callback("Emitting header tone.")
        stream.hz = header_tone
        time.sleep(confirm_tone)
        callback("Emitting data.")
        for i in data:
            stream.hz = i
            time.sleep(tone_speed)
        callback("Emitting confirm tone.")
        stream.hz = confirm_tone
        time.sleep(confirm_speed)
        callback("Emitting complete.")
        stream.hz = 0
        # Disable emitting on stream
        callback_func(None, None)
        stream.EMITTING = False

    # Starting the playing thread
    if LIVE:
        callback("Starting live emitting.")
        x = Thread(target=play_thread)
        x.start()
    else:
        play_data = construct_data()
        stream.play_data = play_data
        stream.PLAYING = True
        stream.play_callback = callback_func
        callback("Playing data.")

import time
import sound.stream as stream
import config
import numpy as np
import math
from threading import Thread
import dict.dictionary as dict

# Getting the constants.
SPS = config.get("sound", "samplerate")
R_VOLUME = config.get("sound", "r_volume")
ROUND = config.get("sound", "round")

# Base variables.
LISTENING = True
header = []
data = []
message_type = ""


def extract_values(indata):
    magnitude = np.abs(np.fft.rfft(indata[:, 0], n=SPS))
    current_vol = np.max(magnitude)
    current_hz = np.argmax(magnitude)
    return current_vol, round(current_hz, ROUND)


def process_recording(record_data, record_time, c_tone, h_tone, t, t_c, p_list, callback_func):
    data_list = []
    for i in record_data:
        vol, hz = extract_values(i[0])
        data_list.append([hz, i[1]/SPS])

    data_list_merged = [data_list[0]]
    for i in range(1, len(data_list)):
        if data_list_merged[-1][0] == data_list[i][0]:
            data_list_merged[-1][1] += data_list[i][1]
        else:
            data_list_merged.append(data_list[i])

    header_found = False
    print(data_list_merged)
    for i in data_list_merged:

        if (i[0] != c_tone and
                i[0] != h_tone and
                i[0] != 0 and
                str(i[0]) not in p_list and
                not header_found):
            for j in range(int(round(round(i[1], 1) / (t), 0))):
                header.append(i[0])
        if i[0] == h_tone and round(i[1], 0) == t_c:
            header_found = True
        if (i[0] != c_tone and
                i[0] != h_tone and
                i[0] != 0 and
                str(i[0]) not in p_list and
                header_found):
            for j in range(int(round(round(i[1], 1) / (t), 0))):
                data.append(i[0])



    # data_list_cleaned = []
    # for i in data_list_merged:
    #     if i[1] >= t/1.1:
    #         data_list_cleaned.append(i)
    #
    # data_list_merged_cleaned = []
    # for i in range(1, len(data_list_cleaned)):
    #     if data_list_merged_cleaned[-1][0] == data_list_cleaned[i][0]:
    #         data_list_merged_cleaned[-1][1] += data_list_cleaned[i][1]
    #     else:
    #         data_list_merged_cleaned.append(data_list_cleaned[i])
    #
    # # Find the beginning of the data
    # for i in range(len(record_data)):
    #     current_vol, current_hz = extract_values(record_data[i])
    #     print(current_hz)
    #     if (current_hz != c_tone and
    #             current_hz != h_tone and
    #             current_hz != 0 and
    #             str(current_hz) not in p_list and
    #             current_vol >= R_VOLUME):
    #         start_idx = i
    #         break
    #
    #
    # # Extract the header
    # for i in range(int(start_idx), len(record_data), math.floor(interval * t)):
    #     current_vol, current_hz = extract_values(record_data[i])
    #     header_found = False
    #     if (current_hz != c_tone and
    #             round(current_hz, -1) != h_tone and
    #             current_hz != 0 and
    #             current_vol >= R_VOLUME and
    #             not header_found):
    #         header.append(current_hz)
    #     if round(current_hz, -2) == h_tone:
    #         header_found = True
    #     if (header_found and
    #             round(current_hz, -2) == h_tone):
    #         start_idx = i
    #         break
    #
    #
    # # Extract the data
    # for i in range(int(start_idx), len(record_data), int(interval * t)):
    #     current_vol, current_hz = extract_values(record_data[i])
    #     if (round(current_hz, -2) != c_tone and
    #             current_hz != 0 and
    #             current_vol >= R_VOLUME):
    #         data.append(current_hz)
    #     else:
    #         break

    print(data, header)
    callback_func(dict.freq_to_test(header), dict.freq_to_test(data))


def record(
        c_tone,
        h_tone,
        t_c,
        t,
        p_list,
        callback_func):
    stream.RECORDING = True
    stream.timer = 0
    stream.sound_buffer = np.array([0])

    # Wait til the confirmation tone
    while stream.get_current_input_hz() != c_tone:
        time.sleep(0.1)

    stream.RECORDING = False
    record_time = stream.timer
    record_data = stream.q[:]
    stream.q = []

    process_recording(record_data, record_time, c_tone, h_tone, t, t_c, p_list, callback_func)


def streaming(
        c_tone,
        h_tone,
        t_c,
        t,
        time_out,
        perf_o,
        callback_func):
    t_o = 0
    while stream.get_current_input_hz() != h_tone and t_o < time_out:
        header.append(stream.get_current_input_hz())
        time.sleep(t / perf_o)
        t_o += t
        if stream.get_current_input_hz() == h_tone:
            print("Header recieved!")
            time.sleep(t_c / perf_o)
            t_o = 0
            while stream.get_current_input_hz() != c_tone and t_o < time_out:
                data.append(stream.get_current_input_hz())
                time.sleep(t / perf_o)
                t_o += t
            if stream.get_current_input_hz() == c_tone:
                print("Data recieved and message end!")
                print(header, data)
                print(dict.freq_to_test(header))
                break


def stream_listen(callback_func):
    global LISTENING
    LISTENING = True

    c_tone = int(config.get("sound", "confirm_tone"))
    h_tone = int(config.get("sound", "header_tone"))
    t_c = config.get("sound", "confirm_speed")
    t = config.get("sound", "tone_speed")
    time_out = config.get("sound", "time_out")
    perf_o = config.get("sound", "performance_overhead")
    p_list = config.get_cat("protocols").keys()

    def listener():
        global header, data, message_type, LISTENING
        header = []
        data = []
        stream.LISTENING = True
        while LISTENING:
            if stream.get_current_input_hz() == c_tone:
                time.sleep(t_c / 2 / perf_o)
                print("Got tone!")
                if stream.get_current_input_hz() == c_tone:
                    time.sleep(t_c / 2 / perf_o)
                    print("Message confirmed!")
                    message_type = stream.get_current_input_hz()
                    print("Message type recieved!")
                    if int(round(message_type, ROUND)) == 400:
                        record(
                            c_tone,
                            h_tone,
                            t_c,
                            t,
                            p_list,
                            callback_func
                        )
                    else:
                        time.sleep(t_c / perf_o)
                        streaming(
                            c_tone,
                            h_tone,
                            t_c,
                            t,
                            time_out,
                            perf_o,
                            callback_func
                        )
                    stream.LISTENING = False
                    break

    # Starting the listening thread
    x = Thread(target=listener)
    x.start()

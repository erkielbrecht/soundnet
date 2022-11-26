import time
import sound.stream as stream
import config
from threading import Thread

import dict.dictionary as dict

LISTENING = True
header = []
data = []
type = ""


def stream_listen():

    global LISTENING
    c_tone = int(config.get("sound", "confirm_tone"))
    h_tone = int(config.get("sound", "header_tone"))
    t_c = config.get("sound", "confirm_speed")
    t = config.get("sound", "tone_speed")
    time_out = config.get("sound", "time_out")
    tone_range = config.get("dictionary", "tone_difference")/2
    perf_o = config.get("sound", "performance_overhead")
    LISTENING = True

    def listener():
        global header, data, type, LISTENING
        header = []
        data = []
        print(tone_range)
        while LISTENING:
            if c_tone-tone_range <= stream.get_current_input_hz() < c_tone+tone_range:
                time.sleep(t_c/2/perf_o)
                print("Got tone!")
                if c_tone-tone_range <= stream.get_current_input_hz() < c_tone+tone_range:
                    time.sleep(t_c/2/perf_o)
                    print("Message confirmed!")
                    type = stream.get_current_input_hz()
                    time.sleep(t_c/perf_o)
                    print("Message type recieved!")
                    t_o=0
                    while not(h_tone-tone_range <= stream.get_current_input_hz() < h_tone+tone_range) and t_o < time_out:
                        header.append(round(stream.get_current_input_hz(), -2))
                        time.sleep(t/perf_o)
                        t_o += t
                    if h_tone-tone_range <= stream.get_current_input_hz() < h_tone+tone_range:
                        print("Header recieved!")
                        time.sleep(t_c/perf_o)
                        t_o=0
                        while not(c_tone-tone_range <= stream.get_current_input_hz() < c_tone+tone_range) and t_o < time_out:
                            data.append(stream.get_current_input_hz())
                            time.sleep(t/perf_o)
                            t_o += t
                        if c_tone-tone_range <= stream.get_current_input_hz() < c_tone+tone_range:
                            print("Data recieved and message end!")
                            print(header,data)
                            print(dict.freq_to_test(header))
                            break

    #Starting the listening thread
    x = Thread(target=listener)
    x.start()
import time
import sound.stream as stream
import config
from threading import Thread

LISTENING = True
header = []
data = []



def listen():
    c_tone = int(config.get("sound", "confirm_tone"))
    h_tone = int(config.get("sound", "header_tone"))
    t_c = int(config.get("sound", "confirm_speed"))
    t = int(config.get("sound", "tone_speed"))

    def listener():
        global header, data
        while LISTENING:
            if c_tone-10 <= stream.get_current_input_hz() < c_tone+10:
                time.sleep(t_c/2)
                if c_tone-10 <= stream.get_current_input_hz() < c_tone+10:
                    time.sleep(t_c/2)
                    print("Message confirmed!")
                    #Placeholder for type
                    time.sleep(t_c)
                    while h_tone-10 <= stream.get_current_input_hz() < h_tone+10:
                        header.append(stream.get_current_input_hz())
                        time.sleep(t)
                    if h_tone-10 <= stream.get_current_input_hz() < h_tone+10:
                        print("Header recieved!")
                        time.sleep(t_c)
                        while c_tone-10 <= stream.get_current_input_hz() < c_tone+10:
                            data.append(stream.get_current_input_hz())
                            time.sleep(t)
                        if c_tone-10 <= stream.get_current_input_hz() < c_tone+10:
                            print("Data recieved and message end!")
                            print(header,data)

    #Starting the listening thread
    x = Thread(target=listener)
    x.start()
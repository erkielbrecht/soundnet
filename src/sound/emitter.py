import config
import dict.dictionary as dict
import stream

def emit(type, header, data):

    type = (type*100)+2000

    confirm_tone = int(config.get("confirm_tone"))
    header_tone = int(config.get("header_tone"))
    tone_speed = int(config.get("tone_speed"))

    data = dict.txt_to_freq(data)
    header = dict.txt_to_freq(header)

    sound_array = [confirm_tone]+[type]+header+[header_tone]+data+[confirm_tone]

    stream.play_array(sound_array, tone_speed)


    


import config
import dict.dictionary as dict
import sound.stream as stream

def emit(type, header, data):
    # Get the type tone corrseponding to a protocol.
    type_tone = config.get(type, 'type_tone')

    # Constants.
    confirm_tone = int(config.get("sound", "confirm_tone"))
    header_tone = int(config.get("sound", "header_tone"))
    tone_speed = config.get("sound", "tone_speed")
    confirm_speed = config.get("sound", "confirm_speed")

    print(tone_speed)

    # Convert data to frequencies.
    data = dict.txt_to_freq(data)
    header = dict.txt_to_freq(header)

    # Emit the data
    stream.emit_data(
        c_tone=confirm_tone, 
        h_tone=header_tone, 
        t_tone=type_tone, 
        header=header, 
        data=data, 
        t=tone_speed, 
        t_c=confirm_speed)


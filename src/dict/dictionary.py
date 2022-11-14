def txt_to_freq(text):
    freq_list = []
    for i in list(text):
        freq_list.append(ord(i)*10+400)
    return freq_list
    
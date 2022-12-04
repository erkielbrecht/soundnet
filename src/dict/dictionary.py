import math

import config

# Remove the ASSCII control characters.
char_amount = 127

# Constants

# How many sounds per character
partition_amount = config.get("dictionary", "partition_amount")
# At which freq the tones start from
tone_baseline = config.get("dictionary", "tone_baseline")
# Step per tone
tone_difference = config.get("dictionary", "tone_difference")


# To find how many different tones we need to cover all chars
def get_tone_partition_size():
    # Unused code for finding reverse variation, if clock method doesn't work
    # x = partition_amount
    # tone_amount = 0
    # while tone_amount < char_amount:
    #    x += 1
    #   tone_amount = math.factorial(x)/math.factorial(x-partition_amount)
    x = math.ceil(char_amount ** (1 / partition_amount))
    return x


# Creates a library of tones corresponding to a char
def get_tone_lib():
    partition_size = get_tone_partition_size()
    iteration = [0, ] * partition_amount
    tone_lib = {}

    for tone in range(char_amount):
        tone_list = []
        for i in iteration:
            tone_list.append((i * tone_difference) + tone_baseline)
        tone_lib[tone + 1] = tone_list
        for i in range(len(iteration)):
            if i == 0:
                iteration[i] += 1
            elif iteration[i - 1] == partition_size:
                iteration[i - 1] = 0
                iteration[i] += 1

    return tone_lib


# Adjusted ord function
def ord_adj(char):
    return ord(char)


# Make text to an array of frequencies.
def txt_to_freq(text):
    freq_list = []
    tone_lib = get_tone_lib()

    for i in list(text):
        freq_list += tone_lib[ord_adj(i)]
    return freq_list


def artefact(text):
    file = open("artefact.txt", 'w')
    file.write(str(txt_to_freq(text)))
    file.close()


def read_artefact():
    file = open("artefact.txt")
    x = list(freq_to_test(file.read()))
    file.close()
    return x


def freq_to_test(data):
    output = ""
    tone_lib = get_tone_lib()
    for i in range(int(len(data) / partition_amount)):
        x = i * 2
        y = (i * 2) + 1
        print(data[x:y + 1])
        try:
            z = list(tone_lib.values()).index(data[x:y + 1])
            output += chr(list(tone_lib.keys())[z])
        except:
            print("Recieved a wrong char")
    return output

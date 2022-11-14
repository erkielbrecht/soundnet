import PySimpleGUI as sg
import sound.stream as sound_stream

def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("request")],
        [sg.Button("Request"),sg.Button("Stop")],
        [sg.Text("0", key="-TEXT-")] 
    ]

def init():
    sound_stream.start_stream()

def listen(event, values, window):
    window['-TEXT-'].update(sound_stream.get_current_input_hz())
    print(sound_stream.get_current_input_hz())
    if event == 'Stop':
            sound_stream.end_stream()
    if event == 'Request':
        sound_stream.play_array([220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850], 0.1)
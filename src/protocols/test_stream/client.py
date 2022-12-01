import PySimpleGUI as sg
import sound.stream as sound_stream
import sound.emitter as em
import sound.listener as ls
import dict.dictionary as dc

def callback(data, header):
    print(data, header)

def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("request")],
        [sg.Button("Request"),sg.Button("Stop")],
        [sg.Text("0", key="-TEXT-")] 
    ]

def callback(header, data):
    print(header, data)

def init():
    sound_stream.start_stream()

def listen(event, values, window):
    window['-TEXT-'].update(sound_stream.get_current_input_hz())
    if event == 'Stop':
        sound_stream.end_stream()
    if event == 'Request':
        em.emit('test_stream', '1234', '1234')
        #ls.stream_listen(callback)
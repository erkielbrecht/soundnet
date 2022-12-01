import PySimpleGUI as sg

import sound.emitter as em
import sound.stream as sound_stream

status = ""


def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("request")],
        [sg.Button("Request"), sg.Button("Stop")],
        [sg.Text("Status:"), sg.Text("0", key="-TEXT-")]
    ]


def callback(header, data):
    print(header, data)


def init():
    sound_stream.start_stream()


def set_status(current_status):
    global status
    status = current_status


def listen(event, values, window):
    window['-TEXT-'].update(status)
    if event == 'Stop':
        sound_stream.end_stream()
    if event == 'Request':
        em.emit(callback, 'test_stream', '1234', '1234', status_callback=set_status)
        # ls.listen(callback)

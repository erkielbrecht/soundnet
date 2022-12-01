import PySimpleGUI as sg

import sound.emitter as em
import sound.stream as sound_stream

# A variable for storing the current status of the program. Useful for testing and debugging.
status = ""


# Layout for your client UI. You can copy this one to start off with.
def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("request")],
        [sg.Button("Request"), sg.Button("Stop")],
        [sg.Text("Status:"), sg.Text("0", key="-TEXT-")]
    ]


# Callback function that gets executed every time an action finishes e.g. listening, emitting.
# Pass this function to listening and emitting calls.
def callback(header, data):
    print(header, data)


# This function gets called when the client is first opened.
# A good practice is to initiate the stream.
def init():
    sound_stream.start_stream()


# A function for setting the feedback listening and emitting plus other tasks.
def set_status(current_status):
    global status
    status = current_status


# Function that listens to the user input from Simple python GUI.
def listen(event, values, window):
    window['-TEXT-'].update(status)
    if event == 'Stop':
        sound_stream.end_stream()
    if event == 'Request':
        em.emit(callback, 'test_stream', '1234', '1234', status_callback=set_status)
        # ls.listen(callback)

import PySimpleGUI as sg

import sound.emitter as em
import sound.listener as ls
import sound.stream as sound_stream

# A variable for storing the current status of the program. Useful for testing and debugging. Try to keep global
# variables to a minimum.
status = ""


# Layout for your client UI. You can copy this one to start off with.
def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("request")],
        [sg.Button("Request"), sg.Button("Stop")],
        [sg.Text("Status:"), sg.Text("", key="-TEXT-")]
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
        em.emit(callback, 'test_stream',
                'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                '1234', status_callback=set_status)
        ls.listen(callback)

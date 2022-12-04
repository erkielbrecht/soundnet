import PySimpleGUI as sg
import time

import sound.emitter as em
import sound.listener as ls
import sound.stream as sound_stream

# A variable for storing the current status of the program. Useful for testing and debugging. Try to keep global
# variables to a minimum.
status = ""
received_data = ""
received_header = ""


# Layout for your client UI. You can copy this one to start off with.
def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("test.txt")],
        [sg.Button("Request"), sg.Button("Stop")],
        [sg.Text("Status:"), sg.Text("", key="-TEXT-")]
    ]


# Callback function that gets executed every time an action finishes e.g. listening, emitting.
# Pass this function to listening and emitting calls.
def callback(header, data):
    global received_data, received_header
    if not header and not data:
        # Listening.
        time.sleep(0.1)
        ls.listen(callback, status_callback=set_status, RECORD=False)
    elif header and not data and header != 'END':
        received_header = header.split(';')
    elif not header and data:
        received_data += data
    elif header == 'END':
        for i in header:
            file = open(f'assets/stream/{i}', 'w')
            file.write(received_data)
            file.close()





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
        em.emit(callback,
                'stream',
                # Define header as request
                'request',
                # The file to be requested
                values[0],
                status_callback=set_status)

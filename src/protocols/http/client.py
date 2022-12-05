import PySimpleGUI as sg
import webbrowser as wb
import os
import time
from datetime import datetime

import config
import sound.emitter as em
import sound.listener as ls
import sound.stream as sound_stream

# A variable for storing the current status of the program. Useful for testing and debugging. Try to keep global
# variables to a minimum.
status = ""
http_status = ""
head_response = ""
ip = ""
METHOD = ""


# Layout for your client UI. You can copy this one to start off with.
def get_layout():
    return [
        [sg.Text('Request a website')],
        [sg.InputText("Address (e.g. test.sound)")],
        [sg.Button("Request"), sg.Button("Request HEAD")],
        [sg.Text("After pressing the button the client first requests the \nserver for dns resolve. \nThen it "
                 "requests the webpage. \nAfter receiving the headers and the data the \nprogram saves it locally and "
                 "opens it in the \ndefault web browser.")],
        [sg.Text("Http status:"), sg.Text("", key="-HTTP-")],
        [sg.Text("Client status:"), sg.Text("", key="-TEXT-")],
        [sg.Text("", key="-HEAD-")]
    ]


# Callback function that gets executed every time an action finishes e.g. listening, emitting.
# Pass this function to listening and emitting calls.
def callback(header, data):
    global http_status, ip, head_response
    # The callback after emitting
    if not header and not data:
        http_status = 'Starting listening.'
        # Listening.
        time.sleep(0.1)
        ls.listen(callback, status_callback=set_status)
    else:
        if header != 'DNS':
            http_status = 'Got an HTTP response!'

            # Save the header data
            file = open(f'assets/http/{ip}/head.txt', 'w')
            file.write(header)

            # Extract the values from the header
            header = {i.split('=')[0]: i.split('=')[1] for i in header.split(';')}

            if data:
                http_status = 'Received a response with a body.'
                data = data.split(';')
                header['Files'] = header['Files'].split(' ')
                print(header)
                for j, i in enumerate(header['Files']):
                    file = open(f'assets/http/{ip}/'+i, 'w')
                    file.write(data[j])
                    file.close()
                wb.open('file://'+os.path.abspath(f'assets/http/{ip}/'+header['Files'][0]), new=2)

            else:
                http_status = 'Received a bodiless response.'
                header_string = ""
                for i in header:
                    header_string += i+': '+str(header[i])+'\n'
                head_response = f'Headers for {ip}\n'+header_string

        elif header == 'DNS':
            http_status = f'Got an DNS response and requesting ip {data}!'
            if data and METHOD != 'HEAD':
                ip = data
                if not(os.path.exists(f'assets/http/{ip}')):
                    os.mkdir(f'assets/http/{ip}')
                if os.listdir(f'assets/http/{ip}'):
                    file = open(f'assets/http/{ip}/head.txt')
                    header = {i.split('=')[0]: i.split('=')[1] for i in file.read().split(';')}
                    header['Files'] = header['Files'].split(' ')
                    file.close()
                    if 'Expires' in header:
                        if datetime.now().replace(second=0, microsecond=0) <= datetime.strptime(header['Expires'],
                                                                                                "%Y-%m-%d %H:%M:%S"):
                            wb.open('file://' + os.path.abspath(f'assets/http/{ip}/' + header['Files'][0]), new=2)

                else:
                    em.emit(callback,
                            # The type of request
                            'http',
                            # Using the set method
                            METHOD,
                            # The user input
                            ip,
                            # Callback for client status
                            status_callback=set_status
                            )
            elif data and METHOD == 'HEAD':
                ip = data
                em.emit(callback,
                        # The type of request
                        'http',
                        # Using the set method
                        METHOD,
                        # The user input
                        ip,
                        # Callback for client status
                        status_callback=set_status
                        )
            else:
                http_status = 'Sorry but the requested webpage could not be found.'


# This function gets called when the client is first opened.
# A good practice is to initiate the stream.
def init():
    print('Http protocol initiated.')
    sound_stream.start_stream()


# A function for setting the feedback listening and emitting plus other tasks.
def set_status(current_status):
    global status
    status = current_status


# Function that listens to the user input from Simple python GUI.
def listen(event, values, window):
    global http_status, METHOD

    window['-TEXT-'].update(status)
    window['-HTTP-'].update(http_status)

    if head_response:
        window['-HEAD-'].update(head_response)

    if event == 'Request':
        http_status = str('Resolving the "IP" for the address', values[0])
        # Using the GET method for a normal request with body
        METHOD = 'GET'
        # Initiates a dns request for the website
        em.emit(callback,
                # The type of request
                'dns',
                # Since we're requesting a webpage we want to resolve for A type record
                'A',
                # The user input
                values[0],
                # Callback for client status
                status_callback=set_status
                )
    if event == 'Request HEAD':
        http_status = 'Resolving the "IP" for the address', values[0]
        # Using the GET method for a normal request with body
        METHOD = 'HEAD'
        # Initiates a dns request for the website
        em.emit(callback,
                # The type of request
                'dns',
                # Since we're requesting a webpage we want to resolve for A type record
                'A',
                # The user input
                values[0],
                # Callback for client status
                status_callback=set_status
                )

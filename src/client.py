import PySimpleGUI as sg

import config
import protocols.http.client as http_client
import protocols.stream.client as stream_client
import protocols.test_stream.client as ts_client
import sound.stream as stream


def run():
    # Operating mode constant
    MODE = ""

    # Layout for choosing operating mode
    choose_layout = [[sg.Text('Choose a protocol for client operations.')],
                     [sg.Button('Test stream'), sg.Button('Http'), sg.Button('Stream')],
                     ]

    # Create the Window
    window = sg.Window('Soundnet ' + config.get("main", "version"), choose_layout, size=(300, 300),
                       element_justification='c')

    # Client loop
    while True:

        event, values = window.read(timeout=100)

        if event == "Test stream":
            new_window = sg.Window('Soundnet ' + config.get("main", "version"), ts_client.get_layout(), size=(300, 300),
                                   element_justification='c', finalize=True)
            window.close()
            window = new_window

            ts_client.init()
            MODE = event

        if event == "Http":
            new_window = sg.Window('Soundnet ' + config.get("main", "version"), http_client.get_layout(),
                                   size=(300, 300),
                                   element_justification='c', finalize=True)
            window.close()
            window = new_window

            http_client.init()
            MODE = event

        if event == "Stream":
            new_window = sg.Window('Soundnet ' + config.get("main", "version"), stream_client.get_layout(),
                                   size=(300, 300),
                                   element_justification='c', finalize=True)
            window.close()
            window = new_window

            stream_client.init()
            MODE = event

        if MODE == "Test stream":
            ts_client.listen(event, values, window)
        elif MODE == "Http":
            http_client.listen(event, values, window)
        elif MODE == "Stream":
            stream_client.listen(event, values, window)

        if event == sg.WIN_CLOSED or event == 'Exit':
            stream.end_stream()
            break

    window.close()

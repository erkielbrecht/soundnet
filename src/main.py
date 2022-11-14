import config
import client
import server

import PySimpleGUI as sg

def main():
    layout = [  [sg.Text('Are you a client or a server?')],
                [sg.Button('Client'), sg.Button('Server'), sg.Button('Exit')] ]

    # Create the Window
    window = sg.Window('Soundnet '+config.get("version"), layout, size=(300,300), element_justification='c')
    while True:
        event, values = window.read()
        if event == "Client":
            window.close()
            client.run()
            break
        if event == "Server":
            window.close()
            server.run()
            break
        if event == sg.WIN_CLOSED or event == 'Exit': 
            break

    window.close()

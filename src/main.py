# Config module accesses values in the config.json folder
# UI
import PySimpleGUI as sg

# Client and server UI as seperate modules.
import client
import config
import server


def main():
    # First layout
    layout = [[sg.Text('Are you a client or a server?')],
              [sg.Button('Client'), sg.Button('Server'), sg.Button('Exit')]]

    # Create the Window
    window = sg.Window('Soundnet ' + config.get("main", "version"), layout, size=(300, 300), element_justification='c')

    while True:
        event, values = window.read()

        if event == "Client":
            window.close()
            client.run()
            break

        if event == "Server":
            window.close()
            server.init()
            server.run()
            break

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

    window.close()

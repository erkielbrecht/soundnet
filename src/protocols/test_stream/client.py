import PySimpleGUI as sg

def get_layout():
    return [
        [sg.Text('Request file')],
        [sg.InputText("request")],
        [sg.Button("Request"),sg.Button("Stop")],
        [sg.Text("0", key="-TEXT-")] 
    ]

def listen(event, values):
    if event == 'Request':
        print(values)
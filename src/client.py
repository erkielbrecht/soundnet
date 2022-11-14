import config
import protocols.test_stream.client as ts_client
import PySimpleGUI as sg
import sound.stream as sound_stream

def run():
    MODE = ""

    choose_layout = [  [sg.Text('Choose a protocol?')],
                [sg.Button('Test stream'), sg.Button('Http')],
                ]

    # Create the Window
    window = sg.Window('Soundnet '+config.get("version"), choose_layout, size=(300,300), element_justification='c')
    while True:
        event, values = window.read(timeout=10)
        if event == "Test stream":
            window1 = sg.Window('Soundnet '+config.get("version"), ts_client.get_layout(), size=(300,300), element_justification='c', finalize=True)
            window.close()
            window = window1
            sound_stream.start_stream()
            MODE = event

        if MODE == "Test stream":
            ts_client.listen(event, values)
            window['-TEXT-'].update(sound_stream.get_current_input_hz())
            print(sound_stream.get_current_input_hz())
            if event == 'Stop':
                sound_stream.end_stream()
            if event == 'Request':
                sound_stream.play_array([220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850,0,220,440,350,330,210,450,670,230,120,300,230,540,210,750,350,850], 0.1)
            
            
        if event == sg.WIN_CLOSED or event == 'Exit': 
            break

    window.close()

import PySimpleGUI as sg

import config
import sound.emitter as em
import sound.listener as ls
from sound.stream import end_stream, start_stream

import protocols.http.server as http_server
import protocols.dns.dns_resolver as dns_resolver

status = ''
protocol_type = ''


def server_listen():
    ls.listen(callback, server_type_callback=set_type, status_callback=set_status)
    pass


def server_emit(type, header, data):
    em.emit(callback, type, header, data, status_callback=set_status)
    pass


def set_status(current_status):
    global status
    status = current_status


def callback(header, data):
    if header and data:
        if protocol_type == 'http':
            http_server.callback(header, data, server_listen, server_emit)
        if protocol_type == 'dns':
            dns_resolver.callback(header, data, server_listen, server_emit)
    else:
        ls.listen(callback_func=callback, status_callback=set_status, server_type_callback=set_type)



def set_type(hz):
    global protocol_type
    protocol_type = config.get("protocols", str(hz))


def init():
    start_stream()


def run():
    ls.listen(callback_func=callback, status_callback=set_status, server_type_callback=set_type)

    server_layout = [[sg.Text('The server is running.')],
                     [sg.Text('Status: '), sg.Text("", key="-TEXT-")]
                     ]

    window = sg.Window('Soundnet ' + config.get("main", "version"), server_layout, size=(300, 300),
                       element_justification='c')

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Exit':
            end_stream()
            break
    window.close()

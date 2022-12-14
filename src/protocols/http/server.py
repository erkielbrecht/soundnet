import os
import time
from datetime import datetime, timedelta

import config


def callback(header, data, server_listen, server_emit):
    time.sleep(float(config.get('http', 'wait_time')))
    ips = os.listdir('assets/http/server')
    if data in ips:
        if header == 'GET':
            files = os.listdir(f'assets/http/server/{data}')
            files.pop(files.index('header.txt'))

            data_data = ''
            for i in files:
                file = open(f'assets/http/server/{data}/{i}')
                data_data += file.read() + ';'
                file.close()

            header_data = open(f'assets/http/server/{data}/header.txt').read() + ';Expires=' + str(
                datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=int(config.get('http', 'expire'))))

            server_emit('http', header_data, data_data)
        elif header == 'HEAD':
            header_data = open(f'assets/http/server/{data}/header.txt').read()

            server_emit('http', header_data, '')
    else:
        server_emit('http', '', '')

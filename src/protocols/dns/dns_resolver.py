import time

import toml

import config


def callback(header, data, server_listen, server_emit):
    records = open('src/protocols/dns/records.toml')
    record_data = toml.load(records, _dict=dict)
    records.close()

    time.sleep(float(config.get('dns', 'wait_time')))

    if record_data[header][data]:
        server_emit('dns', 'DNS', record_data[header][data])
    else:
        server_emit('dns', 'DNS', '')

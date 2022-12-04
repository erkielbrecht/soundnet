import toml


def callback(header, data, server_listen, server_emit):
    records = open('records.toml')
    record_data = toml.load(records, _dict=dict)
    records.close()
    if record_data[header][data]:
        server_emit('dns', 'DNS', record_data[header][data])
    else:
        server_emit('dns', 'DNS', '')

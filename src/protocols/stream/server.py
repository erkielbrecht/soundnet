def callback(header, data, server_listen, server_emit):
    if header:
        file = open(f"assets/stream/{header}")
        file_data = file.read()
        server_emit('stream', '', file_data)

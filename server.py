import socket as sock
import argparse

import settings as sett
import jim

# Parse command-line arguments
parser = argparse.ArgumentParser()


# Create and bind a socket and listed to connections
socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
socket.bind((sett.DEFAULT_LISTEN_ADDRESS, sett.DEFAULT_PORT))
socket.listen()

# Proccess client messages
while True:
    connection, address = socket.accept()
    message = jim.Message.from_str(connection.recv(sett.MAX_DATA_LEN).decode(sett.DEFAULT_ENCODING))
    print(f'Сообщение от {address}: ', message.json)
    if message.action == jim.Actions.PRESENCE:
        response = jim.Response(**jim.Responses.OK.response).json
    else:
        response = jim.Response(**jim.Responses.BAD_REQUEST.response).json
    connection.send(response.encode(sett.DEFAULT_ENCODING))
    connection.close()

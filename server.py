import socket as sock
import argparse

import settings as sett
import jim

# ATTRIBUTES:
# address - server address
# port - server port
# socket - server socket
class Server:
    # initialize parameters and open server socket
    def __init__(self, address: str = None, port: int = None):
        # process parameters
        self.address = address if address else sett.DEFAULT_LISTEN_ADDRESS
        self.port = port if port else sett.DEFAULT_PORT
        print(f"Сервер ожидает соединений по адресу {self.address if self.address else '(все)'}:{self.port}")
        # Create and bind a socket and listed to connections
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen()

    # accept and process client connections
    def accept(self):
        connection, address = self.socket.accept()
        print(f"Установлено соединение с {address}.")
        connection.settimeout(sett.CONNECTION_TIMEOUT)
        try:
            while True:
                data = connection.recv(sett.MAX_DATA_LEN)
                if not data:
                    break
                message = jim.Message.from_str(data.decode(sett.DEFAULT_ENCODING))
                print('Сообщение: ', message.json)
                if message.action == jim.Actions.PRESENCE:
                    response = jim.Response(**jim.Responses.OK.response).json
                else:
                    response = jim.Response(**jim.Responses.BAD_REQUEST.response).json
                connection.send(response.encode(sett.DEFAULT_ENCODING))
        except TimeoutError:
            print(f"Таймаут, соединение с {address} закрывается.")
        else:
            print(f"Соединение с {address} закрыто клиентом.")
        connection.close()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-address', required=False)
    parser.add_argument('-port', required=False)
    args = parser.parse_args()
    # Create a server and start listening
    server = Server(args.address, args.port)
    # Process client messages
    while True:
        server.accept()

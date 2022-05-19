import socket as sock
import argparse

import settings as sett
import jim


# ATTRIBUTES:
# address - server address
# port - server port
# socket - server socket
class Client:
    # initialize parameters and open server socket
    def __init__(self, address: str = None, port: int = None):
        # process parameters
        self.address = address if address else sett.DEFAULT_SERVER_ADDRESS
        self.port = port if port else sett.DEFAULT_PORT
        print(f"Соединение с сервером по адресу {self.address}:{self.port}")
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.connect((self.address, self.port))

    def chat(self):
        message = jim.Message(action=jim.Actions.PRESENCE, type="status",
                              user={
                                  "account_name": "test",
                                  "status": "Online"
                              }
                              )
        self.socket.send(message.json.encode(sett.DEFAULT_ENCODING))
        response = jim.Response.from_str(self.socket.recv(sett.MAX_DATA_LEN).decode(sett.DEFAULT_ENCODING))
        print(f'Сообщение от сервера: ', response.json)
        if response.response == jim.Responses.OK:
            print("Message acknowledged")
        else:
            print(f"Unexpected return code: {response.response}")
        self.socket.close()


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('address', nargs='?', default=None)
    parser.add_argument('port', nargs='?', default=None)
    args = parser.parse_args()
    # Create a client and connect to the server
    client = Client(args.address, args.port)
    # Chat
    client.chat()

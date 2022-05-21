import socket as sock
import argparse
import logging

import settings as sett
import jim
import client_log_config

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
        log.critical("Соединение с сервером по адресу %s:%d", self.address, self.port)
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.connect((self.address, self.port))

    def chat(self):
        message = jim.Message(action=jim.Actions.PRESENCE, type="status",
                              user={"account_name": "test", "status": "Online"}
                              ).json
        log.debug("Отправляется сообщение на сервер: %s", message)
        self.socket.send(message.encode(sett.DEFAULT_ENCODING))
        try:
            data = self.socket.recv(sett.MAX_DATA_LEN).decode(sett.DEFAULT_ENCODING)
            response = jim.Response.from_str(data)
        except ValueError as e:
            log.error("Получен некорректный ответ от сервера (%s): %s", e, data)
        else:
            log.debug("Получено сообщение от сервера: %s", response.json)
            if response.response == jim.Responses.OK:
                log.debug("Сообщение подтверждено.")
            elif response.response == jim.Responses.BAD_REQUEST:
                log.error("Сервер сообщает, что запрос неверен: %s", response.kwargs.get('error', ''))
            else:
                log.error("Неизвестный код возврата от сервера (%s): %s", response.response, data)
        self.socket.close()
        log.critical("Соединение с сервером завершено.")


if __name__ == "__main__":
    print("")
    # Get logger object
    log = logging.getLogger(sett.CLIENT_LOG_NAME)
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('address', nargs='?', default=None)
    parser.add_argument('port', nargs='?', default=None)
    args = parser.parse_args()
    # Create a client and connect to the server
    client = Client(args.address, args.port)
    # Chat
    client.chat()
    print("")

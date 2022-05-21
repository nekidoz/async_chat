import socket as sock
import argparse
import logging

import settings as sett
import jim
import server_log_config


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
        log.critical("Сервер ожидает соединений по адресу %s:%d", self.address if self.address else '(все)', self.port)
        # Create and bind a socket and listed to connections
        self.socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.socket.bind((self.address, self.port))
        self.socket.listen()

    # accept and process client connections
    def accept(self):
        connection, address = self.socket.accept()
        log.info("Клиент %s Соединение установлено.", address)
        connection.settimeout(sett.CONNECTION_TIMEOUT)
        try:
            while True:
                data = connection.recv(sett.MAX_DATA_LEN).decode(sett.DEFAULT_ENCODING)
                if not data:
                    break
                try:
                    message = jim.Message.from_str(data)
                except ValueError as e:
                    log.error("Клиент %s Получен некорректный запрос (%s): %s", address, e, data)
                    response = jim.Response(**jim.Responses.BAD_REQUEST.response).json
                else:
                    log.debug("Клиент %s Получено сообщение: %s", address, message.json)
                    if message.action == jim.Actions.PRESENCE:
                        response = jim.Response(**jim.Responses.OK.response).json
                    else:
                        response = jim.Response(**jim.Responses.BAD_REQUEST.response).json
                log.debug("Клиент %s Отправляется ответ: %s", address, response)
                connection.send(response.encode(sett.DEFAULT_ENCODING))
        except TimeoutError:
            log.info("Клиент %s Соединение закрывается по таймауту.", address)
        else:
            log.info("Клиент %s Соединение закрыто клиентом.", address)
        connection.close()


if __name__ == "__main__":
    print("")
    # Get logger object
    log = logging.getLogger(sett.SERVER_LOG_NAME)
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-address', required=False)
    parser.add_argument('-port', required=False)
    args = parser.parse_args()
    # Create a server and start listening
    server = Server(args.address, args.port)
    # Process client messages
    try:
        while True:
            server.accept()
    except KeyboardInterrupt:
        log.critical("Завершение работы сервера по прерыванию пользователя.")
    print("")

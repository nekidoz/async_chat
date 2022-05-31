import socket as sock
import argparse
import logging
import select
import sys

import settings as sett
import jim
import client_log_config


# ATTRIBUTES:
# _address - server address
# _port - server port
# socket - server socket
# _isConnected - connected-to-server flag
class Client:
    # initialize parameters and open server socket
    def __init__(self, address: str = None, port: int = None):
        # process parameters
        self._address = address if address else sett.DEFAULT_SERVER_ADDRESS
        self._port = port if port else sett.DEFAULT_PORT
        self._isConnected = False
        log.critical("Соединение с сервером по адресу %s:%d", self._address, self._port)
        self._socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        # raise socket.error exception if failed to connect ?
        try:
            self._socket.connect((self._address, self._port))
        except ConnectionRefusedError as e:
            log.critical(f"Соединение с сервером отклонено: {e}")
        except Exception as e:
            log.critical(f"Соединение с сервером не может быть установлено: {e}")
        else:
            log.critical("Соединение с сервером установлено с адреса %s", self._socket.getsockname())
            self._isConnected = True

    @property
    def is_connected(self) -> bool:
        return self._isConnected

    def receive_from_server(self) -> (bool, str):
        """
        Receive data from server
        :return: True if message received and message itself, False otherwise
        """
        success = False                     # prepare for worse
        data = None
        log.debug("Чтение сообщения с сервера.")
        try:
            data = self._socket.recv(sett.MAX_DATA_LEN).decode(sett.DEFAULT_ENCODING)
            if not data:
                log.critical("Соединение закрыто сервером.")
                self._isConnected = False
            else:
                log.debug("Получено сообщение от сервера: %s", data)
                success = True
        except (BrokenPipeError, ConnectionResetError) as e:
            log.critical(f"Нет соединения с сервером: {e}")
            self._isConnected = False
        return success, data

    def send_to_server(self, message: str) -> bool:
        success = False                     # prepare for worse
        log.debug("Отправляется сообщение на сервер: %s", message)
        try:
            self._socket.send(message.encode(sett.DEFAULT_ENCODING))
            received_ok, data = self.receive_from_server()
            if received_ok:
                response = jim.Response.from_str(data)
                if response.response == jim.Responses.OK:
                    log.debug("Сообщение подтверждено.")
                    success = True
                elif response.response == jim.Responses.BAD_REQUEST:
                    log.error("Сервер сообщает, что запрос неверен: %s", response.kwargs.get('error', ''))
                else:
                    log.error("Неизвестный код возврата от сервера (%s): %s", response.response, data)
        except ValueError as e:
            log.error("Получен некорректный ответ от сервера (%s): %s", e, data)
        return success

    def send_presence(self) -> bool:
        message = jim.Message(action=jim.Actions.PRESENCE, type="status",
                              user={"account_name": "test", "status": "Online"}
                              ).json
        return self.send_to_server(message)

    def send_chat_message(self):
        chat_message = input()
        message = jim.Message(action=jim.Actions.MESSAGE,
                              **{"to": "all", "from": "self", "message": chat_message}).json
        return self.send_to_server(message)

    def receive_chat_message(self):
        success = False                     # prepare for worse
        try:
            received_ok, data = self.receive_from_server()
            if received_ok:
                message = jim.Message.from_str(data)

                print("Сообщение от {}: {}".format(message.kwargs['from'], message.kwargs['message']))
                success = True
        except ValueError as e:
            log.error("Получено некорректное сообщение от сервера (%s): %s", e, data)
        except KeyError as e:
            log.error("Получено некорректное сообщение от сервера (%s): %s", e, data)
        return success

    def wait_for_message(self):
        while True:                 # wait for data from stdin or server connection
            print("Введите сообщение: ", end="", flush=True)
            read_ready, _, _ = select.select([sys.stdin, self._socket], [], []) # , sett.CLIENT_SELECT_TIMEOUT
            if not read_ready:
                print("")
                log.debug("Нет новых запросов от существующих соединений.")
            else:
                for connection in read_ready:
                    if connection.fileno() == sys.stdin.fileno():
                        # Send user message to everyone else
                        if not self.send_chat_message():
                            return
                    else:
                        print("")
                        # Receive message sent by someone else
                        if not self.receive_chat_message():
                            return

    def chat(self):
        if not self._isConnected:
            log.critical(f"Обмен сообщениями с сервером невозможен - соединение не установлено.")
            return False
        self.send_presence()
        try:
            self.wait_for_message()
        except KeyboardInterrupt:
            pass
        self._socket.close()
        log.critical("Соединение с сервером завершено.")
        return True


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('address', nargs='?', default=None)
    parser.add_argument('port', nargs='?', default=None)
    args = parser.parse_args()
    # Create a client and connect to the server
    client = Client(args.address, args.port)
    # Chat
    if client.is_connected:
        client.chat()


if __name__ == "__main__":
    print("")
    # Get logger object
    log = logging.getLogger(sett.CLIENT_LOG_NAME)
    # Call main()
    main()
    print("")

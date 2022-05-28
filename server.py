import socket
import select
import argparse
import logging
from dataclasses import dataclass

import settings as sett
import jim
import server_log_config


# particular connection attributes
@dataclass
class Connection:
    # __slots__ = ('chat', 'connection', 'address')       # Optimize memory usage with slots
    chat: jim.Chat                  # chat instance
    connection: socket.socket       # connection instance
    address: (str, int)             # client address

    def fileno(self):
        """ (NOT USED) Return file descriptor to use with select.select() """
        return self.connection.fileno()


class Server:
    """
    ATTRIBUTES:
    address - server address
    port - server port
    socket - server socket
    connections - server connections dictionary with sockets as keys
    """
    def __init__(self, address: str = None, port: int = None):
        """
        Initialize parameters and open a TCP server socket
        :param address: IP address of the interface to wait for client connections on
        :param port: port to wait for client connections on
        If any of the parameters are not specified, defaults are used.
        """
        # process parameters
        self.address = address if address else sett.DEFAULT_LISTEN_ADDRESS
        self.port = port if port else sett.DEFAULT_PORT
        log.critical("Сервер ожидает соединений по адресу %s:%d", self.address if self.address else '(все)', self.port)
        # Create and bind a socket and listed to connections
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.address, self.port))
            self.socket.settimeout(sett.SERVER_SOCKET_TIMEOUT)
            self.socket.listen()
        except OSError as e:
            log.critical("Ошибка инициализации сервера: %s", e)
            exit(-1)
        self.connections = {}

    def _accept_connection(self) -> bool:
        """
        Accept a pending connection if any, if maximum number of connection has not been reached.
        Add a new connection to the connections dictionary.
        :return: True if a new connection accepted, False if timeout or maximum number of connections reached
        """
        if len(self.connections) >= sett.SERVER_MAX_CONNECTIONS:
            return False
        try:
            connection, address = self.socket.accept()
        except TimeoutError:
            log.debug("Нет новых запросов на соединение.")
            return False                # Timeout - no client connection requests available
        else:
            log.info("Клиент %s Соединение установлено.", self.address)
            connection.settimeout(0)
            self.connections[connection] = Connection(
                connection=connection,
                address=address,
                chat=jim.Chat()
            )
            return True

    def _process_message(self, connection: Connection) -> bool:
        """
        For the specified connection, receive a peer's message, process it and reply to it if needed
        :return: True if message exchange succeeded, False if failed for some reason
        """
        try:
            data = connection.connection.recv(sett.MAX_DATA_LEN)
            if not data:
                log.info("Клиент %s Соединение закрыто клиентом.", connection.address)
                return False
            log.debug("Клиент %s Получено сообщение: %s", connection.address, data)
            success, response, forward_list = connection.chat.process_encoded_message(data)
            if not success:
                log.error("Клиент %s %s", connection.address, connection.chat.error_str)
            log.debug("Клиент %s Отправляется ответ: %s", connection.address, response)
            connection.connection.send(response)

            # Forward message to other clients if requested
            if forward_list:
                log.debug("Клиент %s Пересылка сообщения клиентам: %s", connection.address, forward_list)
                for other_connection in self.connections:
                    if other_connection.fileno() != connection.connection.fileno():
                        other_connection.send(data)
            return True
        except TimeoutError:
            log.info("Клиент %s Соединение закрывается по таймауту.", connection.address)
            return False
        except ConnectionResetError:
            log.info("Клиент %s Соединение закрыто клиентом.", connection.address)
            return False

    def _process_messages(self):
        """
        Process all the connections ready to communicate.
        If message exchange with a given connection fails, close it and remove from the connections list.
        :return: None
        """
        read_ready, _, _ = select.select(self.connections, [], [], sett.SERVER_SELECT_TIMEOUT)
        if not read_ready:
            log.debug("Нет новых запросов от существующих соединений.")
        else:
            for connection in read_ready:
                if not self._process_message(self.connections[connection]):
                    connection.close()
                    del self.connections[connection]

    def service_connections(self):
        """ Accept connections and process client messages """
        while True:
            log.debug("Старт цикла обслуживания соединений.")
            print("Существующие соединения: ", end="")
            print(self.connections)
            # Accept all pending connections
            while self._accept_connection():
                pass
            self._process_messages()


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-address', required=False)
    parser.add_argument('-port', required=False)
    args = parser.parse_args()
    # Create a server and start listening
    server = Server(args.address, args.port)
    # Process client messages
    try:
        server.service_connections()
    except KeyboardInterrupt:
        log.critical("Завершение работы сервера по прерыванию пользователя.")


if __name__ == "__main__":
    print("")
    # Get logger object
    log = logging.getLogger(sett.SERVER_LOG_NAME)
    # Call main()
    main()
    print("")

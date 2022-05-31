import socket
import select
import argparse
import logging
import threading
import queue

import settings as sett
import jim
import server_log_config


class Connection(threading.Thread):
    """
    Connection thread class - handles individual client connections
    ATTRIBUTES:
    chat: jim.Chat                  # chat instance
    connection: socket.socket       # connection instance
    address: (str, int)             # client address
    queue: queue.Queue              # client message queue for messages to be processed by the server
    """
    def __init__(self, connection: socket.socket, address: (str, int), message_queue: queue.Queue,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)       # Initialize thread
        self.daemon = True                      # Terminate when the main thread (main()) terminates
        self.connection = connection
        self.address = address
        self.chat = jim.Chat()
        self.queue = message_queue

    def _process_messages(self):
        """
        Receive the peer's message, process it and reply to it if needed.
        :return: True if message exchange succeeded, False if failed for some reason
        """
        try:
            while True:
                data = self.connection.recv(sett.MAX_DATA_LEN)
                if not data:
                    log.info("Клиент %s Соединение закрыто клиентом.", self.address)
                    break
                log.debug("Клиент %s Получено сообщение: %s", self.address, data)
                chat_success, response, forward_list = self.chat.process_encoded_message(data)
                if not chat_success:
                    log.error("Клиент %s %s", self.address, self.chat.error_str)
                log.debug("Клиент %s Отправляется ответ: %s", self.address, response)
                self.connection.send(response)
                # Forward message to server to send it to other clients if requested
                if forward_list:
                    self.queue.put((data, self.connection))
        except TimeoutError:
            log.info("Клиент %s Соединение закрывается по таймауту.", self.address)
        except ConnectionResetError:
            log.info("Клиент %s Соединение закрыто клиентом.", self.address)
        except Exception as e:
            log.critical("Клиент %s Неизвестная ошибка клиента: %s: %s", self.address, type(e), e)

    def run(self):
        log.debug("Клиент %s Поток запущен.", self.address)
        self._process_messages()
        self.connection.close()
        self.queue.put((jim.Message(jim.Actions.QUIT).json.encode(sett.DEFAULT_ENCODING), self.connection))
        log.debug("Клиент %s Поток завершен.", self.address)


class ServiceQueue(threading.Thread):
    """
    ATTRIBUTES:
    connections - client connections dictionary with sockets as keys
    queue - client message queue for messages to be processed by the server
    """
    def __init__(self, message_queue: queue.Queue, connections: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.daemon = True
        self.queue = message_queue
        self.connections = connections

    def service_queue(self):
        """
        Service the client message queue.
        """
        while True:
            log.debug("Ожидание очереди сообщений клиентов")
            message_bytes, connection = self.queue.get()      # Get tuple from queue
            address = self.connections[connection].address
            try:
                message = jim.Message.from_str(message_bytes.decode(sett.DEFAULT_ENCODING))
            except ValueError as e:
                log.error("Клиент %s Некорректное сообщение (%s): %s", address, e, message_bytes)
            else:
                if message.action == jim.Actions.MESSAGE:
                    log.debug("Клиент %s Пересылка сообщения адресатам: %s", address, message_bytes)
                    for other_connection in self.connections:
                        if other_connection.fileno() != connection.fileno():
                            other_connection.send(message_bytes)
                elif message.action == jim.Actions.QUIT:
                    log.info("Клиент %s Соединение закрывается по запросу клиента.", address)
                    connection.close()
                    del self.connections[connection]
                else:
                    log.error("Клиент %s Неподдерживаемый запрос (%s): %s", address, message.action, message_bytes)
            finally:
                self.queue.task_done()

    def run(self):
        self.service_queue()


class Server(threading.Thread):
    """
    ATTRIBUTES:
    address - server address
    port - server port
    socket - server socket
    connections - client connections dictionary with sockets as keys
    queue - client message queue for messages to be processed by the server
    queue_thread - queue processing thread
    !!! IMPLEMENT LOCK ON CONNECTIONS!!!
    """
    def __init__(self, address: str = None, port: int = None, *args, **kwargs):
        """
        Initialize parameters and open a TCP server socket
        :param address: IP address of the interface to wait for client connections on
        :param port: port to wait for client connections on
        If any of the parameters are not specified, defaults are used.
        """
        super().__init__(*args, **kwargs)
        self.daemon = True
        # process parameters
        self.address = address if address else sett.DEFAULT_LISTEN_ADDRESS
        self.port = port if port else sett.DEFAULT_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}
        self.queue = queue.Queue(sett.SERVER_QUEUE_MAXSIZE)
        self.queue_thread = None

    def accept_connections(self):
        """
        Accept connections if maximum number of connection has not been reached,
        otherwise send server error message until number of connections falls below maximum.
        Create a new connection, add it to the connections dictionary and start the new connection's thread.
        :return: None
        """
        while True:
            # Accept connection
            log.debug("Ожидание входящих соединений.")
            print("Существующие соединения: ", end="")
            print(self.connections)
            print(threading.enumerate())
            print(f"Queue size: {self.queue.qsize()}")
            connection, address = self.socket.accept()
            # If maximum number of connections reached, send error message and close connection
            if len(self.connections) >= sett.SERVER_MAX_CONNECTIONS:
                log.warning("Достигнут максимум соединений - %d. Попытка собрать мусор.")
                # delete dead daemons
                self.connections = dict([(key, value) for key, value in self.connections.items() if value.is_alive()])
                if len(self.connections) >= sett.SERVER_MAX_CONNECTIONS:
                    log.error("Клиент %s Отказ в соединении - достигнут максимум (%d).",
                              address, sett.SERVER_MAX_CONNECTIONS)
                    connection.send(jim.Response(jim.Responses.SERVER_ERROR).json.encode(sett.DEFAULT_ENCODING))
                    connection.close()
            else:
                self.connections[connection] = Connection(connection=connection,
                                                          address=address,
                                                          message_queue=self.queue,
                                                          name="Client-" + "-".join([str(token) for token in address]))
                self.connections[connection].start()
                log.info("Клиент %s Соединение установлено (всего %d соединений).",
                         address, len(self.connections))

    def run(self):
        log.critical("Сервер ожидает соединений по адресу %s:%d", self.address if self.address else '(все)', self.port)
        # Bind a socket and listed to connections
        try:
            self.socket.bind((self.address, self.port))
            # self.socket.settimeout(sett.SERVER_SOCKET_TIMEOUT_THREADS)
            self.socket.listen()
        except OSError as e:
            log.critical("Ошибка инициализации сервера: %s", e)
            return
        # Start queue processing thread
        self.queue_thread = ServiceQueue(message_queue=self.queue, connections=self.connections,
                                         name="Queue")
        self.queue_thread.start()
        # Accept incoming connections
        self.accept_connections()


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-address', required=False)
    parser.add_argument('-port', required=False)
    args = parser.parse_args()
    # Create a server thread and start listening
    server = Server(args.address, args.port, name="Server")
    server.start()
    # Process client messages
    try:
        server.join()
    except KeyboardInterrupt:
        log.critical("Завершение работы сервера по прерыванию пользователя.")


if __name__ == "__main__":
    print("")
    # Get logger object
    log = logging.getLogger(sett.SERVER_LOG_NAME)
    # Call main()
    main()
    print("")

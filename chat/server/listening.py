import time
import socket
import logging

from threading import Thread
from chat.server.client import Client


class Listening(Thread):
    """
    Receive client TCP connections
    and create new threads with them
    """

    def __init__(self, server):
        Thread.__init__(self)

        self.server = server
        self.counter = 0
        self.__stop = False

    def set_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Wait for broadcast port to be set in case searching
        # for a proper port lasts
        while not self.server.broadcast.bind_port:
            time.sleep(.1)

        self.sock.bind((self.server.host_ip, self.server.broadcast.bind_port))
        self.sock.listen(self.server.max_clients)

        logging.info(
            msg=f' Server: Listening on host {self.server.host_ip}:,'
                f' port: {self.server.broadcast.bind_port}'
        )

    def run(self):
        self.set_socket()

        while not self.__stop:
            self.sock.settimeout(1)

            client_addr = None

            try:
                client_sock, client_addr = self.sock.accept()
            except socket.timeout:
                client_sock = None

            if client_sock:
                client_thread = Client(
                    server=self.server,
                    sock=client_sock,
                    addr=client_addr,
                    number=self.counter
                )

                self.counter += 1
                self.server.client_threads.append(client_thread)

                client_thread.start()

    def close(self):
        for thr in self.server.client_threads:
            thr.stop()
            thr.join()

        if self.sock:
            self.sock.close()
            self.sock = None

    def stop(self):
        self.__stop = True

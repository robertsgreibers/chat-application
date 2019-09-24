import socket
import select
import logging

from threading import Thread
from chat.constants import Port
from chat.app.serializer import Serializer


class Broadcast(Thread):
    """
    Each server should respond to broadcasts from known subnets with a
    message that contains following information:

    - Server IP
    - Free slots count
    - Server ID
    """

    def __init__(self, server):
        Thread.__init__(self)

        self.server = server
        self.serializer = Serializer()

        self.bind_addr = ''
        self.bind_port = None
        self.sock = None
        self.__stop = False

    def close(self):
        if self.sock:
            self.sock.close()

    def bind_to_port(self):
        bind_port = None

        for port in Port.BROADCAST_RANGE:
            try:
                self.sock.bind((self.bind_addr, port))
                bind_port = port
                break
            except OSError:
                continue

        return bind_port

    def set_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind_port = self.bind_to_port()

        if not self.bind_port:
            self.sock = None
            logging.error(
                msg=f' Could not find valid port to start the server'
            )
            return self.sock

        logging.info(msg=' Wait for client broadcast...')
        logging.info(msg=f' Bind address     : {self.bind_addr}')
        logging.info(msg=f' Bind port        : {self.bind_port}')
        logging.info(msg=f' Server given port: {self.sock.getsockname()[1]}')

        return self.sock

    def run(self):
        if not self.set_socket():
            self.stop()

        while not self.__stop:
            try:
                ready, _, _ = select.select([self.sock], [], [], 2)
            except OSError:
                continue

            if ready:
                data, client_addr = self.sock.recvfrom(1024)
                client_data = self.serializer.deserialize(data)

                logging.info(
                    msg=f' Incoming client broadcast, address: {client_addr}'
                )
                logging.info(
                    msg=f' Incoming client broadcast, data: {client_data}'
                )

                if client_addr[0] not in self.server.addresses:
                    logging.info(
                        msg=f' {client_addr} address not in list of '
                            f'server subnet addresses.'
                    )
                    continue

                self.sock.sendto(
                    self.serializer.serialize(
                        {
                            'id': self.server.id,
                            'ip': self.server.host_ip,
                            'slots': self.server.get_slots_available(),
                        }
                    ),
                    client_addr
                )
        self.close()

    def stop(self):
        self.__stop = True

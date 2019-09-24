import logging
import select
import socket
import time

from chat.constants import Port, Action

from chat.app.serializer import Serializer
from chat.client.read import Read
from chat.client.show import Show
from chat.app.threads import (
    handle_threads_alive,
    handle_threads_stop
)


class Client:

    def __init__(self, nickname, server_id):
        self.nickname = nickname
        self.server_id = server_id

        self.serializer = Serializer()

        self.exit = False

        self.server_addr = None

        self.bad_servers = []

        self.msg_sock = None

        self.threads = []

        self.available_servers = []

    def disconnect_from_server(self):
        """
        If server gets "disconnect" from
        the client, notification to all other clients should also be sent.
        """
        self.msg_sock.sendall(
            self.serializer.serialize(
                {
                    'action': Action.DISCONNECT,
                }
            )
        )
        self.stop()

    def run(self):
        """
        If connection doesn't occur within allowed time (3 seconds),
        client should wait for 4 seconds and start discovery process again.
        """

        if not self.discover():
            logging.error(msg=' Failed to discover proper servers')
            return

        connected = self.connect()

        while not connected:
            logging.info(
                msg=' Wait 4 seconds and restart discovery process'
            )
            time.sleep(4)

            if not self.discover():
                logging.error(msg=' Failed to discover proper servers')
                return

            connected = self.connect()

            if connected:
                break

        self.start_threads()
        self.keep_alive()

    def keep_alive(self):
        """
        If client gets disconnected from the server,
        after 4 seconds it should restart discovery process.
        """

        while self.exit is False:
            time.sleep(1)

            if False not in self.threads_alive():
                continue

            self.stop()

            if self.exit:
                return

            while True in self.threads_alive():
                time.sleep(.1)

            logging.info(
                msg=' Restarting discovery in 4 seconds...'
            )
            time.sleep(4)

            self.run()
            return

    def start_threads(self):
        """
        When client sends a message, it should be sent to all other clients
        connected to the same server (no chat rooms).

        Each client should have a nickname attached to each message.
        Messages should go through the server.

        Client app should get messages from the user via stdin - one line for one message.
        Client app should display each message with nickname
        """

        self.threads = [
            Show(sock=self.msg_sock),
            Read(client=self),
        ]

        for thread in self.threads:
            thread.start()

    def nickname_available(self):
        self.msg_sock.sendall(
            self.serializer.serialize(
                {
                    'action': Action.NICKNAME,
                    'nickname': self.nickname,
                }
            )
        )
        data = self.msg_sock.recv(1024)
        nickname_status = self.serializer.deserialize(data)

        if not nickname_status['available']:
            logging.info(
                msg=f' Sorry nickname \'{self.nickname}\''
                    f' is already taken on server \'{self.server_id}\''
            )
            self.msg_sock.close()
            self.exit = True
            self.stop()

    def connect(self):
        """
        Client chooses one server by id, stops discovery process and
        connects (TCP/IP) to the selected server.

        Client app should not have any inactivity timeouts.

        When connecting to the server, client should wait no
        longer than 3 seconds for connection establishment to occur.
        """

        max_wait = 3
        connected = False

        for server_addr in self.available_servers:
            try:
                self.msg_sock = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )
                self.msg_sock = socket.create_connection(
                    server_addr,
                    timeout=max_wait
                )
                self.nickname_available()
                connected = True
            except (socket.timeout, ConnectionRefusedError):
                self.bad_servers.append(server_addr)
                continue

            if connected:
                break

        if not connected:
            self.msg_sock = None
            self.available_servers = None

        return connected

    def discover(self):
        """
        Client tries to discover all servers in all known subnets by periodic
        (once in 3 sec) broadcast (UDP/IP) till it finds appropriate server.
        """

        time_period = 3

        bind_addr = ''
        bind_port = 0

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind_addr, bind_port))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        logging.info(msg=f' ')
        logging.info(msg=f' Bind address     : {bind_addr}')
        logging.info(msg=f' Bind port        : {bind_port}')
        logging.info(msg=f' Client port   : {sock.getsockname()[1]}')

        for broadcast_port in Port.BROADCAST_RANGE:
            sock.sendto(
                self.serializer.serialize({'nickname': self.nickname}),
                ('<broadcast>', broadcast_port)
            )

            try:
                ready, _, _ = select.select([sock], [], [], time_period)
            except KeyboardInterrupt:
                return

            if not ready:
                continue

            data, server_addr = sock.recvfrom(1024)
            server = self.serializer.deserialize(data)

            # Avoid server if it
            # doesn't match following conditions
            server_conditions = [
                server['id'] == self.server_id,
                server['slots'] > 0,
                server_addr not in self.bad_servers
            ]

            if server['slots'] == 0:
                logging.info(msg=f' {server["id"]} is full.')
                logging.info(msg=f' Looking for other servers...')

            if False not in server_conditions:
                self.available_servers.append(server_addr)
                break

        return self.available_servers

    @handle_threads_alive
    def threads_alive(self):
        pass

    @handle_threads_stop
    def stop(self):
        pass

import time
import select
import logging
import datetime

from threading import Thread
from chat.constants import Action
from chat.app.serializer import Serializer


class Client(Thread):

    def __init__(self, server, sock, addr, number):
        Thread.__init__(self)

        self.server = server

        self.sock = sock
        self.addr = addr
        self.number = number

        self.serializer = Serializer()
        self.last_activity = None
        self.nickname = self.addr
        self.__stop = False

    def stop(self):
        self.last_activity = None
        self.__stop = True

    def close(self):
        if self.sock:
            self.sock.close()

    def set_nickname(self, nickname):
        if self.nickname_not_set() and self.nickname_available(nickname):
            self.nickname = nickname
            self.sock.sendall(
                self.serializer.serialize({
                    'available': True,
                })
            )
            return True
        elif self.nickname_not_set():
            self.sock.sendall(
                self.serializer.serialize({
                    'available': False,
                })
            )
            return False
        else:
            return True

    def get_nickname(self):
        return self.nickname or self.addr

    def nickname_not_set(self):
        return self.nickname == self.addr

    def nickname_available(self, nickname):
        return nickname not in [
            client.nickname for client in self.server.client_threads
        ]

    def set_last_activity(self):
        self.last_activity = datetime.datetime.now()

        logging.info(
            msg=f' {self.get_nickname()}:'
                f' Set last activity to: {self.last_activity}'
        )

    def send(self, content):
        """
        Used to broadcast messages to all connected clients
        """
        self.sock.sendall(self.serializer.serialize(content))

    def run(self):
        self.__stop = False
        self.set_last_activity()

        while not self.__stop:
            try:
                ready, _, _ = select.select([self.sock], [], [])
            except OSError:
                return

            time.sleep(.5)

            if not ready:
                continue

            try:
                data = self.sock.recv(1024)
            except (OSError, ConnectionResetError):
                continue

            try:
                client = self.serializer.deserialize(data)
            except EOFError:
                continue

            self.set_last_activity()

            """
            Server shouldn't allow multiple users with the same nickname
            """
            if client['action'] == Action.NICKNAME:
                if not self.set_nickname(nickname=client['nickname']):
                    return self.server.disconnect_client(client=self)

            """
            If server gets "disconnect" from
            the client, notification to all other clients should also be sent.
            """
            if client['action'] == Action.DISCONNECT:
                self.server.disconnect_client(client=self)
                self.server.send_notification(
                    message=f'{self.get_nickname()} left the server.'
                )
                return

            if client['action'] == Action.MESSAGE:
                logging.info(
                    msg=f' {self.get_nickname()}: {client["message"]}'
                )
                for thr in self.server.client_threads:
                    thr.send(content=client)

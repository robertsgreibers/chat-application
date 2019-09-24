import logging
import select
import time

from threading import Thread
from chat.app.serializer import Serializer


class Show(Thread):

    def __init__(self, sock):
        Thread.__init__(self)

        self.sock = sock
        self.__stop = False
        self.serializer = Serializer()

    def close(self):
        if self.sock:
            self.sock.close()

    def run(self):
        while not self.__stop:
            try:
                ready, _, _ = select.select([self.sock], [], [])
            except (OSError, ValueError):
                return

            time.sleep(.5)

            if not ready:
                continue

            try:
                data = self.sock.recv(1024)
                server = self.serializer.deserialize(data)
            except (EOFError, ConnectionResetError):
                self.stop()
                self.close()
                return

            logging.info(
                msg=f' {server["nickname"]}: {server["message"]}'
            )

        self.sock.close()

    def stop(self):
        self.__stop = True

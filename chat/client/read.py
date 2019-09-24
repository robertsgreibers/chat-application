import logging
import sys
import select
import time

from threading import Thread
from chat.constants import Action
from chat.app.serializer import Serializer


class Read(Thread):

    def __init__(self, client):
        Thread.__init__(self)

        self.client = client
        self.__stop = False
        self.serializer = Serializer()

    def close(self):
        if self.client.msg_sock:
            self.client.msg_sock.close()

    def run(self):
        if not self.client.exit:
            logging.info(msg=' Enter \'exit\' to close connection.')
            logging.info(msg=' Please enter a message.')

        while not self.__stop:
            msg, _, _ = select.select([sys.stdin], [], [], 3)

            time.sleep(.5)

            if not msg and not self.client.msg_sock._closed:
                continue
            elif self.client.msg_sock._closed:
                logging.info(
                    msg=' Sorry you got disconnected'
                )
                return

            if msg:
                msg = sys.stdin.readline().strip()

            if msg == 'exit':
                self.client.exit = True
                self.client.disconnect_from_server()
                return

            try:
                self.client.msg_sock.sendall(
                    self.serializer.serialize(
                        {
                            'action': Action.MESSAGE,
                            'nickname': self.client.nickname,
                            'message': msg
                        }
                    )
                )
            except (BrokenPipeError, OSError):
                continue

    def stop(self):
        self.__stop = True

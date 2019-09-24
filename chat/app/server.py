import time
import logging

from chat.server.broadcast import Broadcast
from chat.server.listening import Listening
from chat.server.activity import Activity

from chat.app.threads import (
    handle_threads_alive,
    handle_threads_stop,
)


class Server:

    def __init__(self, id, host_ip, addresses, max_clients, timeout):
        self.id = id
        self.host_ip = host_ip
        self.addresses = addresses
        self.max_clients = max_clients
        self.timeout = timeout

        self.threads = []
        self.client_threads = []

        self.broadcast = Broadcast(server=self)
        self.listening = Listening(server=self)
        self.activity = Activity(server=self)

    def get_slots_available(self):
        return self.max_clients - len(self.client_threads)

    def disconnect_client(self, client):
        client.stop()
        client.close()
        self.client_threads.remove(client)

    def send_notification(self, message):
        content = {
            'nickname': self.id,
            'message': message
        }
        logging.info(
            msg=f' {self.id}: {content["message"]}'
        )
        for thr in self.client_threads:
            thr.send(content=content)

    def start(self):
        self.threads = [
            self.broadcast,
            self.listening,
            self.activity,
        ]

        for thread in self.threads:
            thread.start()

        time.sleep(2)
        if False not in self.threads_alive():
            logging.info(
                msg=f' \'{self.id}\' Started!'
                    f' Press any ctrl+c to stop the server...'
            )
        while False not in self.threads_alive():
            time.sleep(1)

    @handle_threads_alive
    def threads_alive(self):
        pass

    @handle_threads_stop
    def stop(self):
        pass

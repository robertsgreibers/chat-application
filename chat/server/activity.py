import time
import datetime as dt
from threading import Thread


class Activity(Thread):
    """
    If the client is silent for more than inactivity timeout, it should be
    disconnected by server and notification should be
    sent to all connected clients.
    """

    def __init__(self, server):
        Thread.__init__(self)

        self.server = server
        self.__stop = False

    def close(self):
        pass

    def run(self):
        while not self.__stop:
            for client in self.server.client_threads:
                max_inactivity = dt.datetime.now() - dt.timedelta(
                    seconds=self.server.timeout
                )

                try:
                    too_long = max_inactivity > client.last_activity
                except TypeError:
                    self.__stop = True
                    return

                if too_long:
                    self.server.disconnect_client(client=client)
                    self.server.send_notification(
                        message=f' {client.get_nickname()} got disconnected'
                                f' for inactivity longer than'
                                f' {self.server.timeout} seconds'
                    )

            time.sleep(1)

    def stop(self):
        self.__stop = True

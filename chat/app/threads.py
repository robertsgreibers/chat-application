def handle_threads_alive(func):
    def wrapper(*args, **kwargs):
        """
        Returns list of booleans with thread aliveness.
        Each boolean represents thread and it's status.
        """
        _self = args[0]

        return [thread.is_alive() for thread in _self.threads]

    return wrapper


def handle_threads_stop(func):
    def wrapper(*args, **kwargs):
        """
        Stop all threads and close connections.
        """
        _self = args[0]

        for thread in _self.threads:
            thread.stop()
            thread.close()

            try:
                thread.join()
            except RuntimeError:
                pass

    return wrapper

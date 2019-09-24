import argparse


class Arguments:

    def __init__(self):
        self.parser = argparse.ArgumentParser()

    def get_for_server(self):
        self.parser.add_argument(
            '--id',
            action='store',
            dest='id',
            type=str,
            default='Default room',
            help='Server ID'
        )
        self.parser.add_argument(
            '--timeout',
            action='store',
            dest='timeout',
            type=int,
            default=3,
            help='Client inactivity timeout (seconds)'
        )
        self.parser.add_argument(
            '--ifaddrs',
            action='store',
            dest='ifaddrs',
            type=str,
            nargs='*',
            default=[],
            help='List of interface addresses (CIDR notation) on LOCAL host'
        )
        self.parser.add_argument(
            '--slots',
            action='store',
            dest='slots',
            type=int,
            default=3,
            help='Client limit'
        )
        return self.parser.parse_args()

    def get_for_client(self):
        self.parser.add_argument(
            '--nickname',
            action='store',
            dest='nickname',
            type=str,
            default='Johnnie',
            help='Client nickname'
        )
        self.parser.add_argument(
            '--server',
            action='store',
            dest='server',
            type=str,
            default=None,
            help='Server ID (not IP or hostname)'
        )
        self.parser.add_argument(
            '--ifaddrs',
            action='store',
            dest='ifaddrs',
            type=str,
            nargs='*',
            default=[],
            help='List of interface addresses (CIDR notation) on LOCAL host'
        )
        return self.parser.parse_args()

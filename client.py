import logging
import socket

from chat.arguments import Arguments
from chat.network.subnet import Subnet
from chat.app.client import Client


def main():
    host_ip = socket.gethostbyname(socket.getfqdn())

    logging.basicConfig(level=logging.INFO)
    args = Arguments().get_for_client()
    subnet = Subnet(host_ip=host_ip)

    # Server and client should properly work on host with multiple subnets
    # (of course, if value/list of option "--ifaddrs" valid)
    if not subnet.valid(ifaddrs=args.ifaddrs):
        return

    if not args.server:
        logging.error(
            msg=' You must provide valid Server ID with --server argument'
        )
        return

    Client(
        nickname=args.nickname,
        server_id=args.server,
    ).run()


if __name__ == '__main__':
    main()

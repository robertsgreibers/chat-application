import logging
import socket

from chat.arguments import Arguments
from chat.network.subnet import Subnet
from chat.app.server import Server


def main():
    logging.basicConfig(level=logging.INFO)

    args = Arguments().get_for_server()

    host_ip = socket.gethostbyname(socket.getfqdn())
    subnet = Subnet(host_ip=host_ip)

    # Server and client should properly work on host with multiple subnets
    # (of course, if value/list of option "--ifaddrs" valid)
    if not subnet.valid(ifaddrs=args.ifaddrs):
        return

    # Get valid addresses for all subnets
    addresses = []

    for ifaddr in args.ifaddrs:
        addresses.extend(subnet.get_addresses(ifaddr=ifaddr))

    Server(
        id=args.id,
        host_ip=host_ip,
        addresses=addresses,
        max_clients=args.slots,
        timeout=args.timeout
    ).start()


if __name__ == "__main__":
    main()

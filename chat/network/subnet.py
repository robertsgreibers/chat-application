import logging
import ipaddress as ip


class Subnet:

    def __init__(self, host_ip):
        self.host_ip = host_ip

    def valid(self, ifaddrs):
        """
        Check if host's IP is in user provided
        subnet list
        """
        invalid_subnets = []

        if not ifaddrs:
            logging.error(
                msg=' At least 1 subnet must be provided'
            )
            return False

        for sub in ifaddrs:
            if ip.IPv4Address(self.host_ip) not in ip.ip_network(sub, False):
                invalid_subnets.append(sub)

        if invalid_subnets:
            logging.error(
                msg=' List of following subnets are not valid for this host'
            )
            logging.error(msg=f' {invalid_subnets}')
            return False
        else:
            return True

    @staticmethod
    def get_addresses(ifaddr):
        return [str(addr) for addr in ip.ip_network(ifaddr, False)]

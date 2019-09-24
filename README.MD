===========================================
  Python - chat server/client application
===========================================

Chat system consists of two applications - server and client.
Both applications can have multiple running instances.

Client tries to discover all servers in all known subnets by periodic (once in 3 sec)
broadcast (UDP/IP) till it finds appropriate server. Each server should
respond to broadcasts from known subnets with a message that contains
following information:
    1) IP address of the server - so client can connect to server
    2) Free slots - if there are no free slots, client must avoid such server, but server must drop all new connections
    3) Server id - so client can find server (let's assume that each server has unique id)

Client chooses one server by id, stops discovery process and connects (TCP/IP)
to the selected server. When client sends a message, it should be sent to all
other clients connected to the same server (no chat rooms). Each client should
have a nickname attached to each message.

Messages should go through the server.
If the client is silent for more than inactivity timeout, it should be disconnected
by server and notification should be sent to all connected clients.

If server gets
"disconnect" from the client, notification to all other clients should also be sent.

Client app should not have any inactivity timeouts. When connecting to the server,
client should wait no longer than 3 seconds for connection establishment to
occur. If it doesn't occur within allowed time, client should wait for 4
seconds and start discovery process again. If client gets disconnected from
the server, after 4 seconds it should restart discovery process.

Application usage:
> server.py --ifaddrs <list of interface addresses (CIDR notation) on LOCAL host> --timeout <client inactivity timeout (seconds)> --slots <client limit> --id <server id>
> client.py --ifaddrs <list of interface addresses (CIDR notation) on LOCAL host> --server <server id (not IP or hostname)> --nickname <clients nickname>

Application usage examples:
> host1$ server.py --ifaddrs "10.35.11.111/24" --timeout 10 --slots 5 --id "party"
> host2$ client.py --ifaddrs "192.168.1.123/24" "10.35.11.112/24" --server "party" --nickname "ice"
> host3$ server.py --ifaddrs "10.35.11.113/24" "192.168.1.124/24" --timeout 21 --slots 9 --id "work"
> host4$ client.py --ifaddrs "192.168.1.125/24" --server "work" --nickname "moon"
> host5$ client.py --ifaddrs "10.35.11.114/24" --server "work" --nickname "sun"

Requirements:
    - Object-oriented and threaded/asynchronous programming
    - Based on pure python3, only python's standard library
    - No child processes
    - Graceful program termination
    - JSON serialization
    - Logging
    - Server shouldn't allow multiple users with the same nickname
    - Server and client should properly work on host with multiple subnets (of course, if value/list of option "--ifaddrs" valid)
    - Server may have connections with multiple clients, no connection to another server.
    - Client may have connection only with one server, no connection to another client.
    - Client app should gets messages from the user via stdin - one line for one message.
    - Client app should display each message with nickname

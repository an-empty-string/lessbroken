from . import state
import asyncio
import argparse

import logging
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser("start irc2-ircd")
parser.add_argument("-l", "--listen-on", dest="listen", action="append",
        help="host:port to listen on")

args = parser.parse_args()

loop = asyncio.get_event_loop()
network = state.NetworkState(loop)

listen_addrs = [(j[0], int(j[1])) for j in [i.split(":") for i in args.listen]]
ircd_servers = [loop.run_until_complete(asyncio.start_server(
    network.handle_new_client, host, port)) for host, port in listen_addrs]

try:
    loop.run_forever()

except KeyboardInterrupt:
    for server in ircd_servers:
        server.close()

loop.run_until_complete(asyncio.wait([server.wait_closed()
    for server in ircd_servers]))
loop.close()

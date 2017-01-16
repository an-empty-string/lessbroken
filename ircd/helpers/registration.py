from .isupport import send_isupport
from ..strings import get_string

import logging
logger = logging.getLogger("ircd.helpers.registration")

def send_welcome(client):
    logger.debug("Sending welcome to client {}".format(client.hostmask))
    client.send_numeric("RPL_WELCOME", get_string("welcome").format(
        network=client.network.config["server"]["network"], hostmask=client.hostmask))
    client.send_numeric("RPL_YOURHOST", get_string("yourhost").format(
        host=client.network.config["server"]["name"]))
    send_isupport(client.network, client)

def check_registered(client):
    if client.ident and client.nick:
        client.registered = True
        send_welcome(client)

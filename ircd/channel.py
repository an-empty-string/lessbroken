"""irc2-ircd channel state"""

from .helpers.modes import unparse_modes, channel_modes, highest_prefix
from .strings import get_string
from .utils import chunks

import collections
import datetime

import logging
logger = logging.getLogger("ircd.channel")

class Channel:
    def __init__(self, network, name):
        self.network = network
        self.name = name
        self.clients = collections.defaultdict(str)
        self.modes = {}
        self.ts = datetime.datetime.now()

    @property
    def names_prefix(self):
        if "p" in self.modes:
            return "*"
        if "s" in self.modes:
            return "@"
        return "="

    # send utilities

    def send_names_to(self, client):
        for chunk in chunks(sorted(self.clients.keys(), key=lambda c: c.nick), 20):  # really just arbitrary
            data = " ".join([highest_prefix(self.clients[c]) + c.nick for c in chunk])
            client.send_numeric("RPL_NAMREPLY", self.names_prefix, self.name, data)
        client.send_numeric("RPL_ENDOFNAMES", self.name, get_string("names_done"))

    # permission checks

    def user_can_send(self, client):
        if "n" in self.modes and client not in self.clients:
            return False
        return True

class Channels:
    def __init__(self, network):
        self.network = network
        self.by_name = {}

    def exists(self, name):
        return name in self.by_name

    def get_or_create(self, name):
        if name not in self.by_name:
            logger.info("get_or_create: creating channel {}".format(name))
            self.by_name[name] = Channel(self.network, name)

        return self.by_name[name]

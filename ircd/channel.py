"""irc2-ircd channel state"""

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

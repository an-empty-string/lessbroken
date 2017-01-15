"""irc2-ircd network state"""

from . import channel, client
from .handlers import handler

import logging
logger = logging.getLogger("ircd.state")

import yaml
with open("ircd/data/default_config.yaml") as f:
    default_config = yaml.load(f)

class NetworkState:
    def __init__(self, loop):
        self.loop = loop

        self.clients = client.Clients(self)
        self.channels = channel.Channels(self)
        self.config = default_config
        self.load_modules()

    def load_modules(self):
        # TODO: use config
        handler.load_module("ircd.handlers.pong")
        handler.load_module("ircd.handlers.registration")
        handler.load_module("ircd.handlers.mode")
        handler.load_module("ircd.handlers.whois")
        handler.load_module("ircd.handlers.message")
        handler.load_module("ircd.handlers.unknown")

    async def handle_new_client(self, reader, writer):
        client = self.clients.new(reader, writer)
        logger.debug("Got new client {}".format(client.id))
        while True:
            if client.is_disconnected():
                return

            line = await client.readln()
            await handler.dispatch_to_handlers(self, client, line)

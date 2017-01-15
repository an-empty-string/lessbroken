"""irc2-ircd client state"""

from .numerics import get_numeric
from datetime import datetime
from ircreactor.envelope import RFC1459Message
import asyncio
import uuid

import logging
logger = logging.getLogger("ircd.client")

class Client:
    def __init__(self, network, reader, writer):
        self.network = network
        self.reader = reader
        self.writer = writer

        self.id = str(uuid.uuid4())

        self.registered = False
        self.nick = None
        self.ident = None
        self.realname = None
        self.host = self.writer.get_extra_info("peername")[0]
        self.real_host = self.host
        self.modes = ""
        self.channels = set()

        self.last_ping_sent = None
        self.last_ping_reply = None

    @property
    def hostmask(self):
        return self.nick + "!" + self.ident + "@" + self.host

    @property
    def shared_channel_members(self):
        result = {}
        for channel in self.channels:
            result |= channel.clients
        return result

    # low-level stuff

    def writeln(self, line):
        if not isinstance(line, bytes):
            line = line.encode()
        if not line.endswith(b"\r\n"):
            line += b"\r\n"

        logger.debug("Send[{}]: {}".format(self.id[:8], line))
        self.writer.write(line)

    async def readln(self):
        result = await self.reader.readline()

        logger.debug("Recv[{}]: {}".format(self.id[:8], result))
        return RFC1459Message.from_message(result.decode("UTF-8").strip("\r\n"))

    # message sending to this client

    def send(self, message=None, **kwargs):
        if not isinstance(message, RFC1459Message):
            message = RFC1459Message.from_data(**kwargs)

        self.writeln(message.to_message())

    def send_numeric(self, numeric, *args):
        args = [self.nick if self.registered else "*"] + list(args)
        self.send(source=self.network.config["server"]["name"],
                verb=get_numeric(numeric), params=args)

    # connection maintenance

    def disconnect(self):
        self.network.clients.all_clients.discard(self)
        if self.nick:
            self.network.clients.by_nickname.pop(self.nick, None)

    def is_disconnected(self):
        if self.reader.at_eof():
            self.disconnect()

        return self not in self.network.clients.all_clients

    async def do_ping(self):
        while True:
            self.send(verb="PING", params=[self.id])
            self.last_ping_sent = datetime.now()
            await asyncio.sleep(self.network.config["ping_interval"])

class Clients:
    def __init__(self, network):
        self.network = network

        self.all_clients = set()
        self.by_nickname = dict()

    def new(self, reader, writer):
        client = Client(self.network, reader, writer)
        self.all_clients.add(client)
        return client

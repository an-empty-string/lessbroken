"""irc2-ircd channel state"""

import collections
import datetime
import logging

from .casemap import canonicalize
from .helpers.modes import prefix_sort, highest_prefix, prefix_letters, channel_modes, unparse_modes
from .strings import get_string
from .utils import chunks

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

    @property
    def mode_str(self):
        data = [i for i in self.modes.items() if not isinstance(i[1], list)]
        return unparse_modes([data, []])

    # general utilities

    def client_with_nick(self, nick):
        for client in self.clients:
            if client.nick == nick:
                return client
        return None

    # modes

    def merge_one_mode(self, client, mode, arg, adding):
        if mode in prefix_letters:
            target = self.client_with_nick(arg)
            if not target:
                client.send_numeric("ERR_USERNOTINCHANNEL", arg, self.name,
                        get_string("other_not_on_channel"))
                return None
            else:
                pfstr = self.clients[target]
                if adding: pfstr += mode
                else: pfstr = "".join([i for i in pfstr if i != mode])
                pfstr = prefix_sort(pfstr)
                self.clients[target] = pfstr
                return (mode, arg)
        else:
            listy_modes = channel_modes[0]  # a-type modes
            if mode in listy_modes and mode not in self.modes:
                self.modes[mode] = []

            if adding and mode in listy_modes and arg not in self.modes[mode]:
                self.modes[mode].append(arg)
            elif adding and mode not in listy_modes:
                self.modes[mode] = arg
            elif not adding and mode in listy_modes and arg in self.modes[mode]:
                self.modes[mode].remove(arg)
            elif not adding and mode not in listy_modes and mode in self.modes:
                del self.modes[mode]
            else:
                return None
            return (mode, arg)

    def merge_modes(self, client, parse_result):
        added, removed = parse_result
        results = ([], [])
        for mode, arg in added:
            result = self.merge_one_mode(client, mode, arg, adding=True)
            if result:
                results[0].append(result)

        for mode, arg in removed:
            result = self.merge_one_mode(client, mode, arg, adding=False)
            if result:
                results[1].append(result)

        unparsed_result = unparse_modes(results)
        logger.info("merged modes {} on {}: new modes are {}".format(
            unparsed_result, self.name, self.mode_str))

        client.send_to_channel(self, verb="MODE", params=[self.name] + unparsed_result.split())

    # send utilities

    def send_names_to(self, client):
        for chunk in chunks(sorted(self.clients.keys(), key=lambda c: c.nick), 20):  # really just arbitrary
            data = " ".join([highest_prefix(self.clients[c]) + c.nick for c in chunk])
            client.send_numeric("RPL_NAMREPLY", self.names_prefix, self.name, data)
        client.send_numeric("RPL_ENDOFNAMES", self.name, get_string("names_done"))

    # permission checks

    def user_can_set_mode(self, client):
        return client in self.clients and "o" in self.clients[client]

    def user_can_send(self, client):
        if "n" in self.modes and client not in self.clients:
            return False
        return True

class Channels:
    def __init__(self, network):
        self.network = network
        self.by_name = {}

    def exists(self, name):
        name = canonicalize(name)
        return name in self.by_name

    def get_or_create(self, name):
        cname = canonicalize(name)
        if cname not in self.by_name:
            logger.info("get_or_create: creating channel {}".format(name))
            self.by_name[cname] = Channel(self.network, name)

        return self.by_name[cname]

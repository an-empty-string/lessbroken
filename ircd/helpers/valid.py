import re

def valid_nick(network, nick):
    tm = re.compile(network.config["valid"]["nick"])
    if len(nick) > network.config["limits"]["nicklen"]:
        return False
    if not tm.match(nick):
        return False
    return True

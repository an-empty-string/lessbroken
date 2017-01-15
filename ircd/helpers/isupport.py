from .modes import channel_modes, prefixes
from ..strings import get_string
from ..utils import chunks

def construct_chanlimit(data):
    return ",".join("{}:{}".format(*kv) for kv in data.items())

def construct_prefix(data):
    return "(" + "".join(i[0] for i in data) + ")" + "".join(i[1] for i in data)

def construct_isupport(network):
    c = network.config
    cl = c["limits"]

    isupport = dict(casemapping="rfc1459", awaylen=cl["awaylen"],
        chanlimit=construct_chanlimit(cl["chanlimit"]),
        chanmodes=",".join(channel_modes), modes=cl["modes"],
        channellen=cl["chanlen"], chantypes=c["server"]["chantypes"],
        maxlist=construct_chanlimit(cl["listlimit"]),
        maxtargets=cl["maxtargets"], nicklen=cl["nicklen"],
        prefix=construct_prefix(prefixes), network=c["server"]["network"],
        topiclen=cl["topiclen"])

    return isupport

def send_isupport(network, client):
    tokens = construct_isupport(network)
    tokens = sorted(tokens.items())

    for chunk in chunks(tokens, 13):  # http://modern.ircdocs.horse/#rplisupport-005
        params = ["{}={}".format(k.upper(), str(v)) for k, v in chunk]
        params.append(get_string("are_supported"))
        client.send_numeric("RPL_ISUPPORT", *params)

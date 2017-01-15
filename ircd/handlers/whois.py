"""irc2-ircd client state"""
from .handler import handler
from .utils import require_registered, require_arguments
from ..strings import get_string

@handler(verb="WHOIS")
@require_registered()
@require_arguments(1)
async def whois(network, client, message):
    target = message.params[0]
    if target not in network.clients.by_nickname:
        client.send_numeric("ERR_NOSUCHNICK", target, get_string("unknown_nickname"))
    else:
        target = network.clients.by_nickname[target]
        client.send_numeric("RPL_WHOISUSER", target.nick, target.ident,
                target.host, "*", target.realname)
        client.send_numeric("RPL_WHOISSERVER", target.nick, network.config["server"]["name"],
                "no server desc") # TODO

    client.send_numeric("RPL_ENDOFWHOIS", get_string("whois_done"))

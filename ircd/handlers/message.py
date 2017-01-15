from .handler import handler
from .utils import require_registered, require_arguments
from ..strings import get_string

def do_send(verb, network, client, message):
    targets, text = message.params[:2]
    targets = targets.split(",")[:network.config["limits"]["maxtargets"]]

    for target in targets:
        if any(target.startswith(i) for i in network.config["server"]["chantypes"]):
            if not network.channels.exists(target):
                client.send_numeric("ERR_NOSUCHCHANNEL", target, get_string("unknown_channel"))
            else:
                channel = network.channels.get_or_create(target)
                if channel.user_can_send(client):
                    client.send_to_channel_except_me(channel, verb=verb, params=[target, text])
                else:
                    client.send_numeric("ERR_CANNOTSENDTOCHAN", target, get_string("cannot_send"))

        elif target not in network.clients.by_nickname:
            client.send_numeric("ERR_NOSUCHNICK", target, get_string("unknown_nickname"))
        elif target in network.clients.by_nickname:
            network.clients.by_nickname[target].send(source=client.hostmask,
                    verb=verb, params=[target, text])

@handler(verb=["PRIVMSG", "NOTICE"])
@require_registered()
@require_arguments(2)
async def send_message(network, client, message):
    do_send(message.verb.upper(), network, client, message)

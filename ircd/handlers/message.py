from .handler import handler
from .utils import require_registered, require_arguments
from ..strings import get_string

def do_send(verb, network, client, message):
    target, text = message.params[:2]
    if any(target.startswith(i) for i in network.config["server"]["chantypes"]):
        pass
    elif target not in network.clients.by_nickname:
        client.send_numeric("ERR_NOSUCHNICK", get_string("unknown_nickname"))
    elif target in network.clients.by_nickname:
        network.clients.by_nickname[target].send(source=client.hostmask,
                verb=verb, params=[target, text])

@handler(verb=["PRIVMSG", "NOTICE"])
@require_registered()
@require_arguments(2)
async def send_message(network, client, message):
    do_send(message.verb.upper(), network, client, message)

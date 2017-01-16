from .handler import handler
from .utils import require_registered, require_arguments
from ..strings import get_string
from ..helpers import channel

@handler(verb="JOIN")
@require_registered()
@require_arguments(1)
async def join_channel(network, client, message):
    chantypes = network.config["server"]["chantypes"]
    targets = message.params[0].split(",")[:network.config["limits"]["maxtargets"]]

    for target in targets:
        if any(target.startswith(i) for i in chantypes):
            channel.add_user_to_channel(client, target)
        else:
            client.send_numeric("ERR_NOSUCHCHANNEL", target, get_string("unknown_channel"))

@handler(verb="PART")
@require_registered()
@require_arguments(1)
async def part_channel(network, client, message):
    chantypes = network.config["server"]["chantypes"]
    targets = message.params[0].split(",")[:network.config["limits"]["maxtargets"]]
    reason = message.params[1] if len(message.params) > 1 else "Leaving"
    reason = "Part: {}".format(reason)

    for target in targets:
        if any(target.startswith(i) for i in chantypes):
            if network.channels.exists(target):
                if not channel.remove_user_from_channel(client, target, reason):
                    client.send_numeric("ERR_NOTONCHANNEL", target, get_string("not_on_channel"))
            else:
                client.send_numeric("ERR_NOSUCHCHANNEL", target, get_string("unknown_channel"))
        else:
            client.send_numeric("ERR_NOSUCHCHANNEL", target, get_string("unknown_channel"))

from .handler import handler
from .utils import require_registered, require_arguments
from ..helpers.modes import parse_modes, unparse_modes, NotEnoughArguments, UnknownMode
from ..strings import get_string
import datetime

@handler(verb="MODE")
@require_registered()
@require_arguments(2, soft=True)
async def set_mode(network, client, message):
    chantypes = network.config["server"]["chantypes"]
    target = message.params[0]
    modes = " ".join(message.params[1:])

    if any(target.startswith(i) for i in chantypes):
        if not network.channels.exists(target):
            return client.send_numeric("ERR_NOSUCHCHANNEL", target, get_string("unknown_channel"))

        try:
            parsed = parse_modes(modes, on_channel=True)
        except NotEnoughArguments:
            return client.send_numeric("ERR_NEEDMOREPARAMS", get_string("more_params"))
        except UnknownMode:
            return client.send_numeric("ERR_UNKNOWNMODE", get_string("unknown_mode"))

        channel = network.channels.get_or_create(target)
        if channel.user_can_set_mode(client):
            channel.merge_modes(client, parsed)

    elif target != client.nick:
        client.send_numeric("ERR_USERSDONTMATCH", get_string("users_dont_match"))

    elif target == client.nick:
        try:
            added, removed = parse_modes(modes, on_channel=False)
        except NotEnoughArguments:
            return client.send_numeric("ERR_NEEDMOREPARAMS", get_string("more_params"))
        except UnknownMode:
            return client.send_numeric("ERR_UNKNOWNMODE", get_string("unknown_mode"))

        added_modes, removed_modes = [i[0] for i in added], [i[0] for i in removed]
        client.modes += "".join(added_modes)
        client.modes = "".join(sorted(i for i in client.modes if i not in removed_modes))

        client.send(source=client.hostmask, verb="MODE", params=[client.nick, unparse_modes((added, removed))])

@handler(verb="MODE")
@require_registered()
@require_arguments(1)
async def get_mode(network, client, message):
    chantypes = network.config["server"]["chantypes"]
    target = message.params[0]

    if any(target.startswith(i) for i in chantypes):
        if not network.channels.exists(target):
            return client.send_numeric("ERR_NOSUCHCHANNEL", target, get_string("unknown_channel"))
        channel = network.channels.get_or_create(target)
        mode = channel.mode_str
        client.send_numeric("RPL_CHANNELMODEIS", channel.name, mode)
        client.send_numeric("RPL_CHANNELTSIS", channel.name,
                str(int((channel.ts - datetime.datetime.fromtimestamp(0)).total_seconds())))

    elif target != client.nick:
        client.send_numeric("ERR_USERSDONTMATCH", get_string("users_dont_match"))
    elif target == client.nick:
        client.send_numeric("RPL_UMODEIS", "+" + client.modes)

from .handler import handler
from .utils import require_registered, require_arguments
from ..helpers.modes import parse_modes, unparse_modes, NotEnoughArguments, UnknownMode
from ..strings import get_string
from ircreactor.envelope import RFC1459Message

@handler(verb="MODE")
@require_registered()
@require_arguments(2, soft=True)
async def set_mode(network, client, message):
    chantypes = network.config["server"]["chantypes"]
    target, modes = message.params[:2]

    if any(target.startswith(i) for i in chantypes):
        pass
    elif target != client.nick:
        client.send_numeric("ERR_USERSDONTMATCH", get_string("users_dont_match"))
    elif target == client.nick:
        try:
            added, removed = parse_modes(modes, on_channel=False)
        except NotEnoughArguments:
            client.send_numeric("ERR_NEEDMOREPARAMS", get_string("more_params"))
        except UnknownMode:
            client.send_numeric("ERR_UNKNOWNMODE", get_string("unknown_mode"))

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
        pass
    elif target != client.nick:
        client.send_numeric("ERR_USERSDONTMATCH", get_string("users_dont_match"))
    elif target == client.nick:
        client.send_numeric("RPL_UMODEIS", "+" + client.modes)

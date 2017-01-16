from .handler import handler
from .utils import require_unregistered, require_registered, require_arguments
from ..helpers.registration import check_registered

@handler(verb="USER")
@require_unregistered()
@require_arguments(4)
async def add_user(network, client, message):
    ident, realname = message.params[0], message.params[3]
    client.ident = ident
    client.realname = realname
    check_registered(client)

@handler(verb="NICK")
@require_unregistered(soft=True)
@require_arguments(1)
async def pre_registration_nick(network, client, message):
    nickname = message.params[0]
    if nickname in network.clients.by_nickname:
        client.send_numeric("ERR_NICKNAMEINUSE", nickname)
    else:
        client.nick = nickname
        network.clients.by_nickname[nickname] = client
        check_registered(client)

@handler(verb="NICK")
@require_registered()
@require_arguments(1)
async def post_registration_nick(network, client, message):
    new_nickname = message.params[0]
    old_nickname = client.nick
    old_hostmask = client.hostmask

    if new_nickname in network.clients.by_nickname:
        client.send_numeric("ERR_NICKNAMEINUSE", new_nickname)
    else:
        network.clients.by_nickname[new_nickname] = client
        del network.clients.by_nickname[old_nickname]
        client.nick = new_nickname
        client.send(source=old_hostmask, verb="NICK", params=[new_nickname])
        client.send_shared_channel_members_except_me(source=old_hostmask, verb="NICK",
                params=[new_nickname])

@handler(verb="QUIT")
@require_unregistered(soft=True)
async def quit_preregistration(network, client, message):
    client.send(verb="ERROR", params=["Closing link (preregistration client quit)"])
    client.disconnect()

def do_client_quit(client, message):
    client.send_shared_channel_members_except_me(verb="QUIT", params=[message])
    client.send(source=client.hostmask, verb="QUIT", params=[message])
    client.send(verb="ERROR", params=["Closing link"])
    client.disconnect()

@handler(verb="QUIT")
@require_registered()
@require_arguments(1, soft=True)
async def quit_postregistration_with_reason(network, client, message):
    do_client_quit(client, "Quit: {}".format(message.params[0]))

@handler(verb="QUIT")
@require_registered()
async def quit_postregistration_without_reason(network, client, message):
    do_client_quit(client, "Quit: client disconnecting")

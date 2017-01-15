from .handler import handler, ANY
from ..strings import get_string

@handler(verb=ANY)
async def send_unknown(network, client, message):
    client.send_numeric("ERR_UNKNOWNCOMMAND", get_string("unknown_command").format(message.verb))

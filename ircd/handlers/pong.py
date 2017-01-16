from .handler import handler
from .utils import require_arguments

@handler(verb="PING")
@require_arguments(1)
async def send_pong(network, client, message):
    client.send(verb="PONG", params=[message.params[0]])

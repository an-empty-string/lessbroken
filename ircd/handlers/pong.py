from .handler import handler
from .utils import require_arguments
from ircreactor.envelope import RFC1459Message

@handler(verb="PING")
@require_arguments(1)
async def send_pong(network, client, message):
    client.send(verb="PONG", params=[message.params[0]])

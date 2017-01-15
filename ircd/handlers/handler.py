from ircreactor.envelope import RFC1459Message
from ..pattern import match, ANY
import importlib

import logging
logger = logging.getLogger("ircd.handlers.handler")

handlers = []
modules = {}

def handler(**kwargs):
    """
    Register a handler.

    Handlers are coroutines that take three arguments: a NetworkState object,
    a Client object, and an RFC1459Message object. They are executed in order,
    and when a handler with a pattern matching the message is found and executed,
    search is stopped, unless a truthy value is returned from the handler.
    """
    def decorator(f):
        pattern = RFC1459Message.from_data(**kwargs)
        handlers.append((pattern, f))
        logger.debug("Registered handler for pattern {}".format(pattern.serialize()))
        return f
    return decorator

async def dispatch_to_handlers(network, client, message):
    for pattern, handler in handlers:
        if match(pattern, message):
            result = await handler(network, client, message)
            if not result:
                break

def load_module(module):
    modules[module] = importlib.import_module(module)

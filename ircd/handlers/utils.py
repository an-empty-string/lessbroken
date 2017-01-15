from .. import numerics
from ..strings import get_string
from functools import wraps

def require_registered(soft=False):
    def decorator(f):
        @wraps(f)
        async def wrapper(network, client, message):
            if client.registered:
                return await f(network, client, message)
            else:
                if soft:
                    return True
                client.send_numeric("ERR_NOTREGISTERED", get_string("not_registered"))
        return wrapper
    return decorator

def require_unregistered(soft=False):
    def decorator(f):
        @wraps(f)
        async def wrapper(network, client, message):
            if not client.registered:
                return await f(network, client, message)
            else:
                if soft:
                    return True
                client.send_numeric("ERR_ALREADYREGISTERED", get_string("already_registered"))
        return wrapper
    return decorator

def require_arguments(n, soft=False):
    def decorator(f):
        @wraps(f)
        async def wrapper(network, client, message):
            if len(message.params) < n:
                if soft:
                    return True
                client.send_numeric("ERR_NEEDMOREPARAMS", get_string("more_params"))
            else:
                return await f(network, client, message)
        return wrapper
    return decorator

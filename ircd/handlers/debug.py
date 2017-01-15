from .handler import handler, ANY

@handler(verb=ANY)
async def debug_print(network, client, message):
    print("debug print: ", message)
    return True

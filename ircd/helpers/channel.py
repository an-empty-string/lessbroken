from ..casemap import canonicalize

def user_in_channel(client, channel_name):
    if not client.network.channels.exists(channel_name):
        return False
    return client in client.network.channels.get_or_create(channel_name).clients

def add_user_to_channel(client, channel_name):
    if user_in_channel(client, channel_name):
        return False

    channel = client.network.channels.get_or_create(channel_name)
    channel.clients[client] = "" if channel.clients else "o"
    client.channels.add(channel)
    client.send_to_channel(channel, verb="JOIN", params=[channel.name])
    channel.send_names_to(client)
    return True

def remove_user_from_channel(client, channel_name, reason):
    if not user_in_channel(client, channel_name):
        return False

    channel = client.network.channels.get_or_create(channel_name)
    client.send_to_channel(channel, verb="PART", params=[channel.name, reason])
    channel.clients.pop(client)
    client.channels.remove(channel)

    if not channel.clients:
        client.network.channels.by_name.pop(canonicalize(channel.name))
    return True

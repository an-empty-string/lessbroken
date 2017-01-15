"""irc2-ircd pattern matching"""

from . import casemap

ANY = None

def match_one(pattern, message, mapping='rfc1459'):
    if pattern is ANY:
        return True

    if isinstance(pattern, list) \
        or isinstance(pattern, set) \
        or isinstance(pattern, tuple):
        return casemap.canonicalize(message, mapping) in \
            map(lambda a: casemap.canonicalize(a, mapping), pattern)

    if casemap.compare(pattern, message, mapping):
        return True

    return False

def match_list(pattern, message):
    if len(pattern) > len(message):
        return False

    return all(match_one(item, message[index])
            for index, item in enumerate(pattern))

def match(pattern, message):
    return match_one(pattern.verb, message.verb) \
            and match_one(pattern.source, message.source) \
            and match_list(pattern.params, message.params)

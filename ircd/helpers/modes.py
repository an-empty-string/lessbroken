"""Modes
A-type modes modify a list of addresses.
B-type modes require a parameter on add and remove.
C-type modes require a parameter on add, and don't take one on remove.
D-type modes don't require a parameter.
"""

channel_modes = ("b", "k", "l", "n") # bqeI,k,l,imntps...
user_modes = "iws"

prefixes = (("o", "@"), ("v", "+"))
prefix_letters = "".join(i[0] for i in prefixes)

class NotEnoughArguments(ValueError):
    pass

class UnknownMode(ValueError):
    pass

def prefix_sort(s):
    letters = [i[0] for i in prefixes]
    return "".join(sorted(s, key=letters.index))

def parse_modes(modes, on_channel):
    """
    Return a two-tuple (modes added, modes removed)
    each element will contain a list of two-tuples (mode, argument or None)
    or throws NotEnoughArguments if there are not enough arguments
    or throws UnknownMode if we encounter an unknown mode character
    """
    if on_channel:
        a_type, b_type, c_type, d_type = channel_modes
        b_type += prefix_letters
    else:
        a_type, b_type, c_type = "", "", ""
        d_type = user_modes
    all_modes = a_type + b_type + c_type + d_type

    result = ([], [])

    sp = modes.split(" ", maxsplit=1)
    modes, args = sp[0], []
    if len(sp) > 1:
        args.extend(sp[1].split())

    adding = True
    for character in modes:
        if character == "+":
            adding = True
        elif character == "-":
            adding = False
        elif character not in all_modes:
            raise UnknownMode()
        elif (character in a_type or character in b_type) and not args:
            raise NotEnoughArguments()
        elif character in c_type and adding:
            raise NotEnoughArguments()
        else:
            arg = None
            if character in a_type or character in b_type:
                arg = args.pop(0)
            elif character in c_type and adding:
                arg = args.pop(0)
            result[not adding].append((character, arg))

    return result

def unparse_modes(parse_result):
    added, removed = parse_result

    added_modes = ("+" + "".join(i[0] for i in added)) if added else ""
    removed_modes = ("-" + "".join(i[0] for i in removed)) if removed else ""
    modes = added_modes + removed_modes
    args = " ".join([i[1] for i in added + removed if i[1] is not None])

    return modes + (" " + args if args else "")

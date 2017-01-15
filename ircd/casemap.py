casemaps = {
    'rfc1459': ('{}|', '[]\\')
}

def canonicalize(s, casemap='rfc1459'):
    s = s.lower()
    for char, replacement in zip(*casemaps[casemap]):
        s = s.replace(char, replacement)
    return s

def compare(a, b, casemap='rfc1459'):
    return canonicalize(a, casemap) == canonicalize(b, casemap)

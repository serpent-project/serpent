

def seeded(something):
    if isinstance(something, basestring):
        return [ord(i) for i in something]
    elif isinstance(something, list):
        return something
    else:
        return [something, ]

def sort(a, b):
    return min(a, b), max(a, b)

def between(x, rng):
    """ looks if x is in rng.
        x can be single variable, 2d or 3d
        note: len(rng) determines what is really checked.
    """
    if not isinstance(x, list) and not isinstance(x, tuple):
        x = [x, ]
    dims = len(rng) / 2
    for dim in range(0, min(dims, len(x))):
        a, b = sort(rng[dim * 2], rng[dim * 2 + 1])
        y = x[dim]
        if y < a or y >= b:
            return False
    return True

if __name__ == '__main__':
    print "Testing utils"
    print "true %s" % (between(5, (1, 10)))

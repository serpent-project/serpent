"""
    Caleb is a nice mapping tool which comes with several configuration files.
    
    this script reads out a caleb file and prints out the ark definition
    
    later on, it will transparently parse into arkanlor definitions
"""
from quanum import re_bracket, re_bracket_square

def bracketed(s, b=re_bracket):
    b = b.search(s)
    if not b:
        return ''
    else:
        return b.group()[1:-1]

def read_file_caleb(filename):
    fh = open(filename, 'r')
    lines = fh.readlines()
    groups = {}
    name, group = None, None
    for line in lines:
        line = line.split('#')[0].strip()
        if '[' in line and ']' in line:
            # group
            if name or group:
                groups[name] = group
            name = bracketed(line, re_bracket_square)
            group = []
            continue
        if '(' in line and ')' in line:
            if group is not None:
                group += [bracketed(line)]
            continue
    return groups

def transform_tiles_bnd(filename):
    TILES_BND_ORDER = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'ine', 'ise', 'isw', 'inw']
    unknown = 1
    groups = read_file_caleb(filename)
    output = []
    tilegroups, transitions = {}, {}
    for gnames, lines in groups.items():
        if '-' in gnames:
            name1, name2 = gnames.split('-')
        else:
            name1, name2 = gnames, 'unknown%s' % unknown
            unknown += 1
        name1, name2 = name1.lower(), name2.lower()
        transname = '%s:%s' % (name1, name2)
        output += [ '[%s]' % name1 ]
        output += [ 'map %s' % lines[0] ]
        output += [ '[%s]' % name2 ]
        output += [ 'map %s' % lines[1] ]
        output += [ '[%s:%s]' % (name1, name2) ]
        if not name1 in tilegroups:
            tilegroups[name1] = lines[0]
        if not name2 in tilegroups:
            tilegroups[name2] = lines[1]
        tiles = lines[2].split(' ')
        for i in xrange(len(TILES_BND_ORDER)):
            if transname not in transitions:
                transitions[transname] = {}
            transitions[transname][TILES_BND_ORDER[i]] = tiles[i]
            output += [ '%s %s' % (TILES_BND_ORDER[i], tiles[i]) ]
    return output, tilegroups, transitions

if __name__ == '__main__':
    import os
    lines, tg, t = transform_tiles_bnd(os.path.abspath(os.path.join('../../..', 'scripts/caleb/tiles_bnd.cfg')))
    print "##### Transformation Output ######"
    for key in tg:
        print '[%s]' % key
        print 'map %s' % tg[key]
        print ''
    for key, values in t.items():
        print '[%s]' % key
        # nicer output, more sane to the 01234567 eye
        for cmd in ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'inw', 'ine', 'ise', 'isw']:
            print '%s %s' % (cmd, values[cmd])
        print ''

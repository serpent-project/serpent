# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
   Quanum Postprocessing.
   taking the outer 8 neighbours, quanum tries to do the same thing as
   original dragon, but tries to guess its borders by itself.
   
   It is named after Quanum Q'nor, the king of all earth dragons.

@author: g4b

LICENSE AND COPYRIGHT NOTICE:

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import re, os
from arkanlor.boulder.generators.utils import select_tile
from arkanlor.boulder.generators.const import BLACKMAP
re_bracket = re.compile('\(.+\)')
re_bracket_curly = re.compile('\{.+\}')
re_bracket_square = re.compile('\[.+\]')

def bracketed(s, b=re_bracket):
    b = b.search(s)
    if not b:
        return ''
    else:
        return b.group()[1:-1]

DEFAULT_TRANSITION = {
        'A': None,
        'B': None,
    }

RESERVED_WORDS = ['map', 'natural', 'manmade', 'flat', 'ignore', 'elevation', ]
SHORTCUT_KEYS = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'inw', 'ine', 'ise', 'isw']
SHORTCUTS = {
    'nw':  "_b_aaa_b",
    'ne':  "_b_b_aaa",
    'se':  "aa_b_b_a",
    'sw':  "_aaa_b_b",
    'n':   "_b_a_a_a",
    'e':   "_a_b_a_a",
    's':   "_a_a_b_a",
    'w':   "_a_a_a_b",
    'inw': "baaaaaaa",
    'ine': "aabaaaaa",
    'ise': "aaaabaaa",
    'isw': "aaaaaaba",
    }

def serialize_ab_byte(b):
    """ serializes one ab byte to ab string """
    s = ''
    for x in xrange(8):
        if b & (0x1 << x):
            s += 'a'
        else:
            s += 'b'
    return s

def repr_ab_bytes(bytelist):
    """ represents ab bytes as strings """
    output = []
    for b in bytelist:
        output += [serialize_ab_byte(b)]
    return output

def resolve_ab_bytes(abstring):
    """
        Resolves abstrings into bytes.
        understands _ as placeholder.
        retrieves all permutations possible.
    """
    unknown_bytes = []
    p = 0x0
    for i in xrange(8):
        c = abstring[i]
        if c == 'a':
            p |= (0x1 << i)
        elif c == 'b':
            pass
        elif c == '_':
            unknown_bytes += [0x1 << i]
    # unknown bytes contain all combinations
    import itertools
    l = len(unknown_bytes)
    bytecombis = [p]
    # build perms
    o = 0x0
    for i in xrange(l):
        o |= 0x1 << i
    for perm in xrange(o):
        b = p
        for i in xrange(l):
            if perm & (0x1 << i):
                b |= unknown_bytes[i]
        bytecombis += [b]
    return bytecombis

def read_file(filename):
    """
        simple reader for quanum definition files.
    """
    fh = open(filename, 'r')
    lines = fh.readlines()
    data = {}
    chapter = None #the active chapter
    name = None
    for line in lines:
        # remove comments.
        line = line.split('#')[0].split('//')[0]
        # remove tailing spaces and make it lower
        line = line.strip().lower()
        if not line:
            continue
        # identify chapters
        if '[' in line and ']' in line:
            if chapter and name:
                data[name] = chapter
            chapter = {}
            name = bracketed(line, re_bracket_square)
            continue
        tokens = line.split(' ')
        if tokens and len(tokens) >= 1:
            chapter[tokens[0]] = tokens[1:]
    if chapter and name:
        data[name] = chapter
    return data

def match_octolist(neighbours, alist, blist):
    a, b = 0, 0
    for x in xrange(8):
        n = neighbours[x]
        if n in alist:
            a |= (0x1 << x)
        elif n in blist:
            b |= (0x1 << x)
    return a, b

class QuanumTransition:
    """
        Represents a transition between two groups and what to do.
    """
    def __init__(self, quanum, group1, group2, transitions=None):
        self.quanum = quanum
        self.group1 = group1
        self.group2 = group2
        self.transitions = transitions or {}

    def add_transition(self, code, order):
        self.transitions[code] = order

    def add_instruction(self, cmd, instruction):
        """
            add an instruction directly from the file
        """
        cmd = cmd.lower()
        if cmd in RESERVED_WORDS:
            return # handle reserved words.
        # we assume its an aabb__ string from now on.
        if cmd in SHORTCUT_KEYS:
            # direction shortcuts like nw n
            cmd = SHORTCUTS[cmd]
        else:
            # check our cmd string
            for c in cmd:
                if not c in 'ab_':
                    return
        # cmd now holds an ab_ string.
        # focus on instructions
        order = [] # simplest order is a list of maptiles.
        for token in instruction:
            try:
                order += [int(token, 16)]
            except ValueError:
                print cmd, instruction
                print "Token is invalid in %s: %s" % ('%s:%s' % (
                                                        self.group1.name,
                                                        self.group2.name
                                                        ), token)
        # resolve cmd into ab bytes and add the transitions.
        ab_bytes = resolve_ab_bytes(cmd)
        for b in ab_bytes:
            self.add_transition(b, order)

    def execute_mapset(self, mapblock, rx, ry, tileset):
        if tileset:
            mapblock.tiles_mod[rx, ry] = select_tile(tileset, mapblock.tile_map[rx, ry])

    def apply_transition(self, mapblock, rx, ry, clist):
        alist = self.group1.tiles
        blist = self.group2.tiles
        a, b = match_octolist(clist, alist, blist)
        c = 0xff & ~(a | b)
        if not c:
            if a in self.transitions:
                order = self.transitions[a]
                # standard order is mapset
                if isinstance(order, list):
                    return (self.execute_mapset, mapblock, rx, ry, order)
                else:
                    return order

class QuanumGroup:
    """
        Represents a group of ground tiles.
    """
    def __init__(self, quanum, name, tiles=None):
        self.quanum = quanum
        self.name = name
        self.tiles = tiles or []
        self.transitions = {}
        self._lazy_lookups = []
        self.options = {}

    def make_lazy_lookups(self):
        if self._lazy_lookups:
            for lookup in self._lazy_lookups:
                l = self.quanum.get_group(lookup)
                if l:
                    self.tiles += l.tiles
                else:
                    print "map instruction refers to unknown group %s" % lookup

    def register_transition(self, to_group, transition):
        self.transitions[to_group] = transition

    def add_tile(self, tile):
        if not tile in self.tiles:
            self.tiles += [tile]

    def add_instruction(self, cmd, instruction):
        """
            add any instruction
            for now, we read only the "map" instruction
        """

        if cmd.lower() == 'map':
            # map takes hex numbers and alphanumeric references to other groups
            # it also supports ranges with ..
            map_instr = []
            add_to_last = False
            for i in instruction:
                if i == '..':
                    add_to_last = True
                    continue
                try:
                    i = int(i, 16)
                    if add_to_last:
                        if len(map_instr):
                            for x in range(map_instr[-1], i):
                                map_instr += [x]
                        add_to_last = False
                    map_instr += [i]
                except ValueError:
                    # try to get the group
                    l = self.quanum.get_group(i)
                    if l:
                        map_instr += l.tiles
                    else:
                        self._lazy_lookups += [i]
            # add our map_instr
            self.tiles += map_instr
        elif cmd.lower() in RESERVED_WORDS:
            self.options[cmd.lower()] = True


##############################################################################
class QuanumQnor:
    """
        Main Post Processor
    """
    def __init__(self, directory=None):
        self._reverse = None
        self.groups = {}
        self.transitions = {}
        if directory:
            self.load_directory(directory)

    def load_directory(self, directory):
        STD_FILES = ['groups.txt']
        try:
            for f in STD_FILES:
                self.add_file(os.path.join(directory, f))
        except:
            raise
        for f in os.listdir(directory):
            if f.lower().endswith('.txt') and f.lower() not in STD_FILES:
                self.add_file(os.path.join(directory, f))

    def build_reverse(self):
        """
            builds the reverse lookup table
            identifying each tile by group
        """
        rev = {}
        for name, group in self.groups.items():
            tiles = group.tiles
            for tile in tiles:
                oldgroups = rev.get(tile, None)
                if oldgroups:
                    rev[tile] += [group]
                else:
                    rev[tile] = [group]
        self._reverse = rev

    def update_reverse(self):
        if self._reverse is None:
            self.build_reverse()

    def apply(self, mapblock, levels=None):
        self.update_reverse() # does nothing if not needed.
        jobs = []
        for rx in xrange(8):
            for ry in xrange(8):
                gs = self._reverse.get(mapblock.tiles[rx, ry], [])
                for g in gs:
                    if g and g.transitions:
                        # i am in a group, check my transitions
                        clist = mapblock.surrounding_tiles(rx, ry)
                        found = None
                        for gname, transition in g.transitions.items():
                            found = transition.apply_transition(
                                                mapblock, rx, ry,
                                                clist=clist,)
                            if found is not None:
                                jobs += [found]
                                break
        # execute all jobs.
        for job in jobs:
            job[0](*job[1:])

    def get_group(self, name):
        if name in self.groups:
            return self.groups[name]

    def get_groups_by_tile(self, tile):
        self.update_reverse()
        if tile in self._reverse:
            return self._reverse[tile]

    def add_file(self, filename):
        definitions = read_file(filename)
        # build groups
        for key, value in definitions.items():
            if ':' in key or '>' in key or '<' in key:
                continue
            # key holds name of group, value holds instructions.
            q = QuanumGroup(self, key)
            for cmd, token in value.items():
                q.add_instruction(cmd, token)
            self.groups[key] = q
        # build transitions
        for key, value in definitions.items():
            if ':' in key or '>' in key or '<' in key:
                if ':' in key:
                    # groupname1:groupname2, value holds instructions
                    name1, name2 = key.split(':')
                elif '>' in key:
                    name1, name2 = key.split('>')
                elif '<' in key:
                    name1, name2 = key.split('<')
                q = QuanumTransition(self, self.get_group(name1),
                                       self.get_group(name2))
                for cmd, token in value.items():
                    q.add_instruction(cmd, token)
                # save this transitions globally:
                self.transitions['%s:%s' % (name1, name2)] = q
                if '<' in key:
                    print "Standard Transition from %s to %s" % (name1, name2)
                    self.get_group(name1).register_transition(name2, q)
            else:
                g = self.get_group(key)
                if g:
                    g.make_lazy_lookups()
        self.build_reverse()

if __name__ == '__main__':
    import os
    THIS_DIR = os.path.abspath(os.path.dirname(os.path.join(os.getcwd(), __file__)))
    QUANUM_SCRIPT_DIR = os.path.abspath(os.path.join(THIS_DIR, '../../../scripts/quanum/'))
    q = QuanumQnor(QUANUM_SCRIPT_DIR)
    for key, group in q.groups.items():
        print "%s -> %s" % (key, group.tiles)
        for key2, trans in group.transitions.items():
            print "%s:%s found" % (key, key2)

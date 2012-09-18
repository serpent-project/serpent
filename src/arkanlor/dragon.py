# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Arkanlor Dragon Engine

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
import os.path, os

COMMENT = -1
STRING = -2 # unknown string.
PATTERN = -3
EMPTY = 0

def unhex(s):
    return int(s, 16)

class DragonScriptFile:

    def __init__(self, filename, scriptdata=None):
        self.filename = filename
        self.scriptdata = scriptdata or []
        self.fh = None
        if filename:
            self.open(filename)

    def is_hex(self, s):
        # check this token if its hex.
        if len(s) == 2 or len(s) == 4:
            for c in s:
                if c not in '0123456789abcdefABCDEF':
                    return False
            return True
        return False

    def is_dec(self, s):
        if len(s) == 3 or '-' in s:
            try:
                i = int(s)
            except ValueError:
                return False
            return True
        return False

    def is_pattern(self, s):
        if len(s) == 8:
            for c in s:
                if c not in 'aAbB':
                    return False
            return True
        return False

    def open(self, filename):
        self.fh = open(filename, 'r')

    def read(self):
        if self.fh:
            lines = self.fh.readlines()
            self.scriptdata = self.parse(lines)
            return self.scriptdata

    def parse(self, lines):
        ret = []
        for line in lines:
            line = line.strip()
            if line.startswith('//'):
                ret += [ (COMMENT, line[2:]) ]
                continue
            # remove comments if there are any
            if '//' in line:
                line, comment = line.split('//', 1)
                print "Inline comment removed: %s" % comment
            tokens = line.split(' ')
            l = 0
            new_line = []
            for token in tokens:
                # try guessing my token type
                if not token:
                    # ignore me
                    continue
                if self.is_pattern(token):
                    l = PATTERN
                    new_line += [token]
                elif self.is_hex(token):
                    new_line += [unhex(token)]
                elif self.is_dec(token):
                    new_line += [int(token)]
                elif isinstance(token, basestring):
                    new_line += [token]
                else:
                    # string.
                    l = STRING
                    new_line = [line]
                    break
                if l >= 0:
                    l += 1
            if l != 0:
                ret += [[l] + new_line]
        return ret

    def print_parsed(self, parsed_lines=None):
        if parsed_lines == None:
            parsed_lines = self.scriptdata
        for line in parsed_lines:
            dtype, data = line[0], line[1:]
            if dtype == COMMENT:
                print '//Comment: %s' % data
                continue
            elif dtype == STRING:
                print '//String: %s' % data
                continue
            elif dtype == 'PATTERN':
                print 'Pattern detected'
            if isinstance(data, basestring):
                print data
            else:
                print 'len: %s (' % dtype + '%s ' * len(data) % tuple(data) + ')'

class DragonTiles:
    def __init__(self, parent, group, color):
        self.parent = parent
        self.group = group
        self.color = color
        self.alt = 0
        self.tiles = []
        self.scripts = []

    def __unicode__(self):
        return u"<DragonTiles Group (%s) Color (%s) Alt(%s), Tiles: %s>" % \
                        (self.group, self.color, self.alt, len(self.tiles))

class DragonGroups:
    def __init__(self):
        self.groups = {}

    def get_group_list(self):
        return self.groups.keys()

    def add_group(self, group, color):
        if group not in self.groups.keys():
            self.groups[group] = []
        self.groups[group] += [DragonTiles(self, group, color)]

    def get_by_groupcolor(self, group, color):
        group = self.groups.get(group, None)
        if group is not None:
            for t in group:
                if t.color == color:
                    return t
    def get_by_color(self, color):
        for key in self.groups:
            t = self.get_by_groupcolor(key, color)
            if t is not None:
                return t
    def get_by_groupalt(self, group, alt):
        # tries to find the first alt you hit.
        group = self.groups.get(group, None)
        if group is not None:
            # get the group which beats the alt.
            for t in group:
                if t.alt >= alt:
                    return t
            # no group beats the alt, lets return the last.
            return t

    def printout(self):
        for key, group in self.groups.items():
            print "Group (%s)" % key
            print group

    def __unicode__(self):
        return "<Dragon Groups %s>" % (len(self.groups),)



class DragonScripts:
    def __init__(self, folder=None):
        self.folder = folder
        self.files = {}
        self.groups = {}
        if folder:
            self.load()

    def load_file(self, name, loc):
        self.files[name] = DragonScriptFile(loc)
        self.files[name].read()
        #setattr(self, name, self.files[name].read())

    def load(self):
        needed_files = {'groups': os.path.join(self.folder, 'groups.txt'),
                        'maptrans': os.path.join(self.folder, 'maptrans.txt'),
                        'items': os.path.join(self.folder, 'items.txt'),
                        'betweentrans': os.path.join(self.folder, 'betweentrans.txt'),
                        'betweentrans2': os.path.join(self.folder, 'betweentrans2.txt'),
                        'statbetweentrans': os.path.join(self.folder, 'statbetweentrans.txt'),
                        'statbetweentrans2': os.path.join(self.folder, 'statbetweentrans2.txt'),
                        'statbetweentrans3': os.path.join(self.folder, 'statbetweentrans3.txt'),
                         }
        for key, value in needed_files.items():
            self.load_file(key, value)
        self.construct_filters()

    def construct_filters(self):
        """
            1. read groups. eventually.
            2. read maptrans for each group.
            3. read all the map stage translations
            4. read all the static stage translations
            
            the goal is to have all filters in the groups signed
            and being able to call for a filtering via providing a mapblock
            or a cell
            
        """
        groups = self.read_groups(self.files['groups'])

        self.read_maptrans(self.files['maptrans'], groups)

        self.groups = groups
        return groups

    def read_groups(self, dfile):
        """
            returns a dict, containing groups as keys, values holding lists of
            colors
        """
        groups = DragonGroups()
        for data in dfile.scriptdata:
            t, data = data[0], data[1:]
            if t == 2:  # all valid group entries are 2 numbers.
                color, group = data
                groups.add_group(group, color)
        return groups

    def read_maptrans(self, dfile, groups):
        """
            //[index position in hex] [index group in hex] [altitude in dec] [tileid1] [tileid2]... [tileidx]
        """
        for data in dfile.scriptdata:
            t, data = data[0], data[1:]
            if t >= 4:
                color, group, alt, tiles = data[0], data[1], data[2], data[3:]
                tileg = groups.get_by_groupcolor(group, color)
                if not tileg:
                    print "No Tilegroup for group %s color %s" % (hex(group), hex(color))
                    continue
                tileg.alt = alt
                tileg.tiles = tiles


if __name__ == '__main__':

    # defining root for our python modules
    THIS_DIR = os.path.abspath(os.path.dirname(os.path.join(os.getcwd(), __file__)))
    DRAGON_SCRIPT_DIR = os.path.abspath(os.path.join(THIS_DIR, '../../scripts/dragon/'))
    dragon = DragonScripts(DRAGON_SCRIPT_DIR)
    #for key in dragon.files.keys():
    #    print "#" * 80
    #    print "## %s" % key
    #    dragon.files[key].print_parsed()
    #    print "#" * 80


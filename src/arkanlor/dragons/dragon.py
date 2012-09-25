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
from arkanlor.boulder.generators.utils import select_tile

COMMENT = -1
STRING = -2 # unknown string.
PATTERN = -3
EMPTY = 0

LAYER_MAP = 0
LAYER_STATIC = 1
LAYER_ITEM = 2
MAP_RUNLEVELS = [0, 1]
STATIC_RUNLEVELS = [2, 3, 4]
ITEM_RUNLEVELS = [5, ] # appropriate,items are lists of 5.
ALL_RUNLEVELS = MAP_RUNLEVELS + STATIC_RUNLEVELS + ITEM_RUNLEVELS

def unhex(s):
    return int(s, 16)

class DragonScriptFile:

    def __init__(self, name, filename, scriptdata=None):
        self.name = name
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
            return self

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

    def __unicode__(self):
        return u"<DragonTiles Group (%s) Color (%s) Alt(%s), Tiles: %s>" % \
                        (hex(self.group), self.color, self.alt, len(self.tiles))

    def __repr__(self):
        return self.__unicode__()

class Filter8:
    def __init__(self, mask, directive):
        if isinstance(mask, basestring):
            # this is an ab mask
            mask = self.resolve_pattern(mask)
        self.mask = mask
        # read height manipulations from directive.
        self.random_range = directive[-2:]
        self.directive = directive[:-2]
    def resolve_pattern(self, pattern):
        b = 0x0
        for c in pattern.upper():
            b = b << 1
            if c == 'B':
                b |= 0x1
        return b
    def serialize_mask(self):
        ret = ''
        for x in xrange(8):
            i = 0x1 << x
            if i & self.mask:
                ret += 'B'
            else:
                ret += 'A'
        return ret
    def execute(self, mapblock, rx, ry, layer=0):
        # execute the directives of this filter on cell rx ry.
        if layer == LAYER_MAP:
            # map layer
            mapblock.tiles_mod[rx, ry] = select_tile(self.directive, mapblock.tile_map[rx, ry])
            # if random_range: add random_range.
            # mapblock.heights[rx, ry] += numpy.randint(*self.random_range)
        elif layer == LAYER_STATIC:
            art = select_tile(self.directive, mapblock.tile_map[rx, ry])
            mapblock.add_static(rx, ry, art, z=mapblock.heights[rx, ry])

class FilterSet:
    def __init__(self):
        self.filters = {}

    def apply_filters(self, mapblock, rx, ry,
                            clist=[],
                            alist=[],
                            blist=None,
                            layer=LAYER_MAP
                            ):
        """
            clist represents the children of this block.
            if they are in blist, they are 1,
            if they are in alist, they are 0
            if they are in neither, it breaks.
            note if alist and blist are none, it does nothing.
        """
        if alist == None:
            return False
        # build our pattern.
        p = 0x0
        o = 0x0
        for x in xrange(8):
            p = p << 1
            o = o << 1
            if clist[x] in alist:
                continue
            elif blist is None:
                return False # disable it for now.
            elif (clist[x] in blist):
                p |= 1
            else:
                o |= 1
        # 0, 2, 4, 6 bits are mandatory.

        # we have our pattern.
        # lets see if we have a filter for this.
        if p in self.filters.keys():
            #print "Found pattern %s %s" % (p, self.filters[p].serialize_mask())
            return (self.filters[p].execute, mapblock, rx, ry, layer)
        return False

    def add_filter8(self, mask, directive):
        filter8 = Filter8(mask, directive)
        self.filters[filter8.mask] = filter8


class DragonGroups:
    def __init__(self):
        self.groups = {}
        self.runs = {} # saves filtersets, connecting two groups.
        self.items = {} # saves item placements per group.
        self._reverse = {} # allows to reverse scan tiles for groups.

    def build_reverse(self):
        rev = {}
        for key, v in self.groups.items():
            tiles = self.get_group_tiles(key)
            for tile in tiles:
                better_key = rev.get(tile, key)
                rev[tile] = min(better_key, key)
        self._reverse = rev

    def update_reverse(self):
        if self._reverse:
            return
        else:
            self.build_reverse()

    def get_group_list(self):
        return self.groups.keys()

    def add_group(self, group, color):
        if group not in self.groups.keys():
            self.groups[group] = []
        self.groups[group] += [DragonTiles(self, group, color)]
        return self.groups[group][-1]

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

    def get_group_tiles(self, group, guess=True):
        if guess:
            # just guess by first alt group.
            return self.groups.get(group)[0].tiles
        else:
            # be theral. build all group tiles
            group = self.groups.get(group, None)
            if group is not None:
                tiles = []
                for tileset in group:
                    tiles += tileset.tiles
                    tiles = list(set(tiles))
                return tiles
        return []

    def connect_groups_by_filterset(self, source, other, filterset, run=0):
        # build our connection index key.
        if not run in self.runs:
            self.runs[run] = {}
        if not source in self.runs[run]:
            self.runs[run][source] = {}
        if not other in self.runs[run][source]:
            self.runs[run][source][other] = []
        self.runs[run][source][other] += [filterset]

    def place_items(self, group, mapblock, rx, ry):
        max_chance = 0x1000
        if group in self.items.keys():
            # 
            chance = self.items[group]['chance']
            item_combis = self.items[group]['items']
            if (mapblock.height_map[rx, ry] * max_chance) < chance:
                items = select_tile(item_combis, mapblock.tile_map[rx, ry])
                for item in items:
                    artid, z, color, rrx, rry = item
                    mapblock.add_static_overflow(rx + rrx, ry + rry,
                                                 artid, z, color)

    def scan_mapblock(self, mapblock, runlevel=0):
        """
            Scan a mapblock and apply filters to it.
        """
        run = self.runs.get(runlevel, None)
        if runlevel in STATIC_RUNLEVELS:
            layer = LAYER_STATIC
        elif runlevel in MAP_RUNLEVELS:
            layer = LAYER_MAP
        elif runlevel in ITEM_RUNLEVELS:
            layer = LAYER_ITEM
        else:
            layer = runlevel
        self.update_reverse() # does nothing if not needed.
        jobs = []
        for rx in xrange(8):
            for ry in xrange(8):
                g = self._reverse.get(mapblock.tiles[rx, ry], None)
                if g is not None:
                    if not run:
                        if layer == LAYER_ITEM:
                            self.place_items(g, mapblock, rx, ry)
                        continue
                    others = run.get(g, None)
                    if others:
                        # i know this group has filters to several others.
                        # i get the children of this mapblock.
                        clist = mapblock.surrounding_tiles(rx, ry)
                        found = False
                        #print "Found others."
                        for other in others:
                            # lets see if any of the filtersets apply something
                            filtersets = others[other]
                            blist = None
                            if other:
                                blist = self.get_group_tiles(other)
                            alist = self.get_group_tiles(g)
                            for filterset in filtersets:
                                found = filterset.apply_filters(
                                            mapblock, rx, ry,
                                            clist=clist,
                                            alist=alist,
                                            blist=blist,
                                            layer=layer,
                                            )
                                if found:
                                    jobs += [found]
        for job in jobs:
            job[0](*job[1:])


    def printout(self):
        for key, group in self.groups.items():
            print "Group (%s)" % key
            print group
        self.update_reverse()
        for rev, v in self._reverse.items():
            print "Item %s in Group %s" % (hex(rev), hex(v))
        for group, itemlist in self.items.items():
            print group, itemlist

    def __unicode__(self):
        return "<Dragon Groups %s>" % (len(self.groups),)



class DragonScripts:
    def __init__(self, folder=None):
        self.folder = folder
        self.files = {}
        self.filters = {}
        self.groups = {}
        if folder:
            self.load()

    def apply(self, mapblock, levels=None):
        if levels is None:
            levels = xrange(2)
        for level in levels:
            self.groups.scan_mapblock(mapblock, level)

    #### Loading mechanism ####

    def load_file(self, name, loc):
        try:
            self.files[name] = DragonScriptFile(name, loc)
            self.files[name].read()
        except IOError:
            pass

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
        groups = DragonGroups()
        if 'groups' in self.files:
            groups = self.read_groups(self.files['groups'], groups)

        self.read_maptrans(self.files['maptrans'], groups)

        self.groups = groups
        # next: read out all subscripts and build filtersets.
        my_f = lambda x: os.path.join(self.folder, x)
        def read_filter_files(level, directory):
            for f in os.listdir(my_f(directory)):
                if f.lower().endswith('.txt'):
                    self.read_filterfile(DragonScriptFile('%s/%s' % (level, f.lower().replace('.txt', '')),
                                                          my_f('%s/%s' % (directory, f))).read())
        read_filter_files(0, 'map')
        read_filter_files(1, 'map2')
        read_filter_files(2, 'statics')
        read_filter_files(3, 'statics2')
        read_filter_files(4, 'statics3')
        # next: read betweentranses and connect filter relations.
        self.read_connections(self.files['betweentrans'], groups, 0)
        self.read_connections(self.files['betweentrans2'], groups, 1)
        self.read_connections(self.files['statbetweentrans'], groups, 2)
        self.read_connections(self.files['statbetweentrans2'], groups, 3)
        self.read_connections(self.files['statbetweentrans3'], groups, 4)

        item_cache = self.read_items(self.files['items'], groups)
        def read_item_files(group, f):
            self.read_itemfile(DragonScriptFile('items/%s' % (f.lower().replace('.txt', '')),
                                                my_f('items/%s' % f)).read(),
                                groups,
                                group)
        for group, item_entry in item_cache.items():
            read_item_files(group, item_entry['file'])
        return groups

    def read_groups(self, dfile, groups):
        """
            returns a dict, containing groups as keys, values holding lists of
            colors
        """
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
                    tileg = groups.add_group(group, color)
                tileg.alt = alt
                tileg.tiles = tiles

    def read_filterfile(self, dfile):
        # reads a filterfile, then creates a filterset.
        if dfile is None:
            return
        filterset = None # lazy creation
        for data in dfile.scriptdata:
            t, data = data[0], data[1:]
            if t == PATTERN:
                # we found ourselves a pattern.
                mask, directive = data[0], data[1:]
                if filterset is None:
                    # create our filterset now.
                    filterset = FilterSet()
                filterset.add_filter8(mask, directive)
        if filterset:
            # save our filterset now.
            self.filters[dfile.name] = filterset

    def read_connections(self, dfile, groups, runlevel):
        # reads a 'connection' 
        for data in dfile.scriptdata:
            t, data = data[0], data[1:]
            if t == 2:
                # None 2 this
                group, filename = data
                other = None
            elif t == 3:
                group, other, filename = data
            else:
                continue
            # find our filterset.
            name = '%s/%s' % (runlevel, filename.lower().replace('.txt', ''))
            filterset = self.filters.get(name, None)
            if filterset:
                groups.connect_groups_by_filterset(group, other, filterset)

    def read_items(self, dfile, groups):
        for data in dfile.scriptdata:
            t, data = data[0], data[1:]
            if t == 7:
                # we do not respect boundaries.
                # [SourceGroup] [ChanceToPlace] [Left] [Top] [Right] [Bottom] [Filename]
                group, chance, filename = data[0], data[1], data[-1]
                groups.items[group] = {'chance': chance,
                                       'items': [],
                                       'file': filename,
                                       }
        return groups.items

    def read_itemfile(self, dfile, groups, group):
        """
            reads an itemfile.
            Syntax :
            [Frqequency] [ItemGroup1] [ItemGroup2] [ItemGroup3] ... 
            Itemgroup = [Item(hex)] [ZLevel(dec)] [Color(hex)] [Xmovement(dec)] [Ymovement(dec)]
        """
        for data in dfile.scriptdata:
            t, data = data[0], data[1:]
            if (t - 1) % 5 == 0:
                frequency, data = data[0], data[1:]
                tiles = []
                while len(data):
                    artid, z, color, rrx, rry, data = data[0], data[1], data[2], data[3], data[4], data[5:]
                    tiles += [[artid, z, color, rrx, rry]]
                for x in xrange(frequency):
                    groups.items[group]['items'] += [tiles]


if __name__ == '__main__':

    # defining root for our python modules
    THIS_DIR = os.path.abspath(os.path.dirname(os.path.join(os.getcwd(), __file__)))
    DRAGON_SCRIPT_DIR = os.path.abspath(os.path.join(THIS_DIR, '../../../scripts/uodev/'))
    dragon = DragonScripts(DRAGON_SCRIPT_DIR)
    print dragon.groups.printout()
    #for key in dragon.files.keys():
    #    print "#" * 80
    #    print "## %s" % key
    #    dragon.files[key].print_parsed()
    #    print "#" * 80


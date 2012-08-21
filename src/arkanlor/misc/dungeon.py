#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Donjon Port to Python
    
    @author drow http://donjon.bin.sh/
    @author g4b
"""
import numpy

#control
MAX_ROOMS = 999

# configuration
DUNGEON_LAYOUTS = {
    'box': [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
    'cross': [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    }

CORRIDOR_LAYOUTS = {
    'labyrinth': 0,
    'bent': 50,
    'straight': 100,
    }
MAP_STYLE = {
    'default': {
        'fill': 0x000000,
        'open': 0xFFFFFF,
        'open_grid': 0xCCCCCC,
    }
    }

# cell bitmask
NOTHING = 0x00000000
BLOCKED = 0x00000001
ROOM = 0x00000002
CORRIDOR = 0x00000004
#                 0x00000008
PERIMETER = 0x00000010
ENTRANCE = 0x00000020
ROOM_ID = 0x0000FFC0

ARCH = 0x00010000
DOOR = 0x00020000
LOCKED = 0x00040000
TRAPPED = 0x00080000
SECRET = 0x00100000
PORTC = 0x00200000
STAIR_DN = 0x00400000
STAIR_UP = 0x00800000

LABEL = 0xFF000000

OPENSPACE = ROOM | CORRIDOR
DOORSPACE = ARCH | DOOR | LOCKED | TRAPPED | SECRET | PORTC
ESPACE = ENTRANCE | DOORSPACE | 0xFF000000
STAIRS = STAIR_DN | STAIR_UP

BLOCK_ROOM = BLOCKED | ROOM
BLOCK_CORR = BLOCKED | PERIMETER | CORRIDOR
BLOCK_DOOR = BLOCKED | DOORSPACE

def seeded(something):
    if isinstance(something, basestring):
        return [ord(i) for i in something]
    elif isinstance(something, list):
        return something
    else:
        return [something, ]

class Dungeon(object):
    def __init__(self, seed, width, height,
                 rooms=None,
                 min_rooms=3,
                 max_rooms=9,
                 **opts
                 ):
        self.seed = seeded(seed)
        self.cx = int(width / 2)
        self.cy = int(height / 2)
        self.width = self.cx * 2
        self.height = self.cy * 2
        self.max_rooms = max_rooms
        self.min_rooms = min_rooms
        default_opts = {
            'room_layout': 'scattered',
            'corridor_layout': 'bent',
            'remove_deadends': 50,
            'add_stairs': 2,
            'map_style': 'default',
            'dungeon_layout': '',
                     }
        print opts
        for k, v in opts.items():
            default_opts[k] = v
        self.opts = default_opts
        print self.opts
        self.rooms = rooms or {}
        self.num_rooms = len(self.rooms)
        self.room_base = int((min_rooms + 1) / 2)
        self.room_radix = int((max_rooms - min_rooms) / 2) + 1

    def ascii_output(self):
        output = []
        for y in xrange(self.height):
            line = ''
            for x in xrange(self.width):
                ch = '?'
                c = self.cells[x, y]
                if c == NOTHING:
                    ch = '_'
                if c & BLOCKED:
                    ch = '.'
                if c & ROOM:
                    ch = 'o'
                if c & CORRIDOR:
                    ch = '='
                if c & PERIMETER:
                    ch = '|'
                if c & ENTRANCE:
                    ch = 'A'
                line += ch
            output += [line]
        for line in output:
            print line

    def init_cells(self):
        self.cells = numpy.zeros((self.width, self.height), dtype=int)
        for x in xrange(self.width):
            for y in xrange(self.height):
                self.cells[x, y] = NOTHING
        numpy.random.seed(self.seed)
        self.setup_layout_mask(self.opts.get('dungeon_layout'))

    def setup_layout_mask(self, layout=None):
        if layout in DUNGEON_LAYOUTS.keys():
            self.mask_cells(DUNGEON_LAYOUTS[layout])
        elif layout == 'round':
            self.mask_round()

    def mask_cells(self, mask, maskbit=BLOCKED):
        mask = numpy.array(mask)
        mx = len(mask) * 1.0 / self.width
        my = len(mask[0]) * 1.0 / self.height
        for x in xrange(self.width):
            for y in xrange(self.height):
                if mask[x * mx, y * my]:
                    self.cells[x, y] |= maskbit

    def mask_round(self, maskbit=BLOCKED):
        for x in xrange(self.width):
            for y in xrange(self.height):
                d = numpy.sqrt(((x - self.cx) ** 2) + ((y - self.cy) ** 2))
                if d > self.cy:
                    self.cells[x, y] |= maskbit

    def emplace_rooms(self):
        if self.opts.get('room_layout', 'scattered') == 'packed':
            self.pack_rooms()
        else:
            self.scatter_rooms()

    def set_room(self, proto=None):
        proto = proto or {}
        if not proto.get('width', None):
            if proto.get('x', None):
                a = self.cx - self.room_base - proto['x']
                if a <= 0: a = self.room_radix
                r = a if (a <= self.room_radix) else self.room_radix
                proto['width'] = int(numpy.random.randint(0, r)) + self.room_base
            else:
                proto['width'] = int(numpy.random.randint(0, self.room_radix)) + self.room_base
        if not proto.get('height', None):
            if proto.get('y', None):
                a = self.cy - self.room_base - proto['y']
                if a <= 0: a = self.room_radix
                r = a if (a <= self.room_radix) else self.room_radix
                proto['height'] = int(numpy.random.randint(0, r)) + self.room_base
            else:
                proto['height'] = int(numpy.random.randint(0, self.room_radix)) + self.room_base
        # note: setting missing x and y here is a new random number, even if height has been randomized already!
        # this seems faulty. maybe move to top?
        if not proto.get('x', None):
            proto['x'] = int(numpy.random.randint(0, self.cx) - proto['width'])
        if not proto.get('y', None):
            proto['y'] = int(numpy.random.randint(0, self.cx) - proto['height'])
        return proto

    def sound_room(self, x1, y1, x2, y2):
        hit = {}
        for x in range(x1, x2):
            for y in range(y1, y2):
                if self.cells[x, y] & BLOCKED:
                    return None
                elif self.cells[x, y] & ROOM:
                    id = self.cells[x, y] & ROOM_ID >> 6
                    hit[id] = hit.get(id, 0) + 1
        return hit


    def emplace_room(self, proto=None):
        if self.num_rooms >= MAX_ROOMS:
            return
        proto = self.set_room(proto)
        # room boundaries
        x1, y1 = proto['x'] * 2 + 1, proto['y'] * 2 + 1
        x2, y2 = ((proto['x'] + proto['width']) * 2 - 1,
                 (proto['y'] + proto['height']) * 2 - 1)
        if (x1 < 1) or x2 > self.width or y1 < 1 or y2 > self.height:
            return
        hit = self.sound_room(x1, y1, x2, y2)
        if hit is None:
            return
        hit_list = hit.keys()
        if len(hit_list) == 0:
            room_id = self.num_rooms + 1
            self.num_rooms = room_id
        else:
            return
        self.opts['last_room_id'] = room_id

        # --- emplacement --
        for x in range(x1, x2):
            for y in range(y1, y2):
                if (self.cells[x, y] & ENTRANCE):
                    self.cells[x, y] &= ~ESPACE
                elif (self.cells[x, y] & PERIMETER):
                    self.cells[x, y] &= ~PERIMETER
                self.cells[x, y] |= ROOM | (room_id << 6)
        height = ((x2 - x1) + 1) * 10
        width = ((y2 - y1) + 1) * 10
        room_data = {
            'id': room_id,
            'x': x1, 'y': y1,
            'north': y1, 'south': y2, 'west': x1, 'east': x2,
            'height': height, 'width': width,
            'area': (height * width)
            }
        self.rooms[room_id] = room_data
        # block corridors from room boundary
        # check for door openings from adjacent rooms
        for x in range(x1 - 1, x2 + 1):
            try:
                if not (self.cells[x, y1 - 1] & (ROOM | ENTRANCE)):
                    self.cells[x, y1 - 1] &= PERIMETER
            except IndexError:
                pass
            try:
                if not (self.cells[x, y2 + 1] & (ROOM | ENTRANCE)):
                    self.cells[x, y2 + 1] &= PERIMETER
            except IndexError:
                pass

        for y in range(y1 - 1, y2 + 1):
            try:
                if not (self.cells[x1 - 1, y] & (ROOM | ENTRANCE)):
                    self.cells[x1 - 1, y] &= PERIMETER
            except IndexError:
                pass
            try:
                if not (self.cells[x2 + 1, y] & (ROOM | ENTRANCE)):
                    self.cells[x2 + 1, y] &= PERIMETER
            except IndexError:
                pass

    def pack_rooms(self):
        for x in xrange(self.cx):
            r = (x * 2) + 1
            for y in xrange(self.cy):
                c = (y * 2) + 1
                if self.cells[r, c] & ROOM:
                    continue
                if (x == 0 or y == 0) and numpy.random.randint(0, 2):
                    continue
                self.emplace_room({'x': x, 'y': y})

    def possible_rooms(self):
        """ alloc rooms in donjon, number of possible rooms """
        dungeon_area = self.width * self.height
        room_area = self.max_rooms * self.max_rooms
        return int(dungeon_area / room_area)


    def scatter_rooms(self):
        for i in xrange(self.possible_rooms()):
            self.emplace_room()

    def open_rooms(self):
        pass


def main():
    dungeon = Dungeon('arkane sanctum', 100, 55,
                      min_rooms=12,
                      max_rooms=32,
                      dungeon_layout='crest',
                      anything='possible',
                      room_layout='packed')
    dungeon.init_cells()
    dungeon.emplace_rooms()
    dungeon.ascii_output()

if __name__ == '__main__':
    main()

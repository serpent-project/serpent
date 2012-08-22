#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Donjon Port to Python
    
    @author drow http://donjon.bin.sh/
    @author g4b (python port and modifications)
"""
# note: r=y=i=height, c=x=j=width
# while translating to python, i chose to use x/y and w/h only mostly
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

WEST = 'west'
NORTH = 'north'
EAST = 'east'
SOUTH = 'south'

OPPOSITE_DIRS = {
  NORTH: SOUTH, SOUTH: NORTH,
  WEST: EAST, EAST: WEST
  }

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# stairs

STAIR_ENDS = {
  NORTH: {
    'walled' : [[1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1]],
    'corridor' : [[0, 0], [1, 0], [2, 0]],
    'stair' : [0, 0],
    'next' : [1, 0],
  },
  SOUTH: {
    'walled' : [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1]],
    'corridor':[[0, 0], [-1, 0], [-2, 0]],
    'stair' :[0, 0],
    'next' :[-1, 0],
  },
  WEST: {
    'walled': [[-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1]],
    'corridor': [[0, 0], [0, 1], [0, 2]],
    'stair': [0, 0],
    'next': [0, 1],
  },
  EAST: {
    'walled' : [[-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]],
    'corridor' :[[0, 0], [0, -1], [0, -2]],
    'stair' : [0, 0],
    'next':[0, -1],
  },
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# cleaning

CLOSE_ENDS = {
  NORTH :  {
    'walled' :  [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1]],
    'close' :  [[0, 0]],
    'recurse' :  [-1, 0],
  },
  SOUTH:  {
    'walled' :  [[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1]],
    'close' :  [[0, 0]],
    'recurse' :  [1, 0],
  },
  WEST:  {
    'walled' :  [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0]],
    'close' :  [[0, 0]],
    'recurse' :  [0, -1],
  },
  EAST:  {
    'walled' :  [[-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0]],
    'close' :  [[0, 0]],
    'recurse' :  [0, 1],
  },
}

DOORY = { NORTH:-1, SOUTH: 1,
          WEST: 0, EAST:  0 }
DOORX = { NORTH:  0, SOUTH:  0,
          WEST:-1, EAST:  1 }


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

def sort(a, b):
    return min(a, b), max(a, b)

class Dungeon(object):
    def __init__(self, seed, width, height,
                 rooms=None,
                 min_rooms=3,
                 max_rooms=9,
                 **opts
                 ):
        self.connect = None
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
        for k, v in opts.items():
            default_opts[k] = v
        self.opts = default_opts
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
                    ch = 'o'
                if c & BLOCKED:
                    ch = 'X'
                if c & ROOM:
                    ch = '-'
                if c & CORRIDOR:
                    ch = '~'
                if c & PERIMETER:
                    ch = '+'
                if c & ENTRANCE:
                    ch = '%'
                if c & DOORSPACE:
                    ch = 'H'
                line += ch
            output += [line]
        for line in output:
            print line

    def init_cells(self):
        """ initialize the dungeon buffer """
        self.cells = numpy.zeros((self.width, self.height), dtype=int)
        for x in xrange(self.width):
            for y in xrange(self.height):
                self.cells[x, y] = NOTHING
        numpy.random.seed(self.seed)
        self.setup_layout_mask(self.opts.get('dungeon_layout'))

    def setup_layout_mask(self, layout=None):
        """ setup the mask of the dungeon by layout """
        if layout in DUNGEON_LAYOUTS.keys():
            self.mask_cells(DUNGEON_LAYOUTS[layout])
        elif layout == 'round':
            self.mask_round()

    def mask_cells(self, mask, maskbit=BLOCKED):
        """ mark cells by a mask, (2 dim array) """
        mask = numpy.array(mask)
        mx = len(mask) * 1.0 / self.width
        my = len(mask[0]) * 1.0 / self.height
        for x in xrange(self.width):
            for y in xrange(self.height):
                if mask[x * mx, y * my]:
                    self.cells[x, y] |= maskbit

    def mask_round(self, maskbit=BLOCKED):
        """ mark cells by a circled mask """
        for x in xrange(self.width):
            for y in xrange(self.height):
                d = numpy.sqrt(((x - self.cx) ** 2) + ((y - self.cy) ** 2))
                if d > self.cy:
                    self.cells[x, y] |= maskbit

    def emplace_rooms(self):
        """ places the rooms according to rules """
        if self.opts.get('room_layout', 'scattered') == 'packed':
            self.pack_rooms()
        else:
            self.scatter_rooms()

    def set_room(self, proto=None):
        """ create a random rectangular room and ensure position and dimensions """
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
        """ returns a dictionary containing all rooms a rectangle hits """
        hit = {}
        for x in range(x1, x2):
            for y in range(y1, y2):
                if self.cells[x, y] & BLOCKED:
                    return None
                elif self.cells[x, y] & ROOM:
                    id_ = self.cells[x, y] & ROOM_ID >> 6
                    hit[id_] = hit.get(id_, 0) + 1
        return hit


    def emplace_room(self, proto=None):
        """ emplace a room, if no proto given, define a new one
            ensures boundary check and creates a perimeter.
        """
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
            'area': (height * width),
            'door_treshhold': lambda x: 1, # modify this lambda to get multidoors
            }
        self.rooms[room_id] = room_data
        # block corridors from room boundary
        # check for door openings from adjacent rooms
        for x in range(x1 - 1, x2 + 1):
            try:
                if not (self.cells[x, y1 - 1] & (ROOM | ENTRANCE)):
                    self.cells[x, y1 - 1] |= PERIMETER
            except IndexError:
                pass
            try:
                if not (self.cells[x, y2] & (ROOM | ENTRANCE)):
                    self.cells[x, y2] |= PERIMETER
            except IndexError:
                pass

        for y in range(y1 - 1, y2 + 1):
            try:
                if not (self.cells[x1 - 1, y] & (ROOM | ENTRANCE)):
                    self.cells[x1 - 1, y] |= PERIMETER
            except IndexError:
                pass
            try:
                if not (self.cells[x2, y] & (ROOM | ENTRANCE)):
                    self.cells[x2, y] |= PERIMETER
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
        for i in range(1, self.num_rooms):
            self.open_room(self.rooms[i])
        self.connect = None

    def check_sill(self, room, x, y, dir):
        """
            check a doorsill for correctness and prepare a door.
            returns none if door is not placeable
            returns {x,y,dir,door_x,door_y,out_id} if it is
        """
        door_x = x + DOORX[dir]
        door_y = y + DOORY[dir]
        # if door is not in a perimeter or block_door, return
        if not self.cells[door_x, door_y] & PERIMETER:
            return
        elif self.cells[door_x, door_y] & BLOCK_DOOR:
            return
        out_x = door_x + DOORX[dir]
        out_y = door_y + DOORY[dir]
        # block check
        if self.cells[out_x, out_y] & BLOCKED:
            return
        out_id = None
        if self.cells[out_x, out_y] & ROOM:
            # save the id of our door's room.
            out_id = self.cells[out_x, out_y] & ROOM_ID >> 6
            if out_id == room['id']:
                # room into itself should not exist.
                return
        return {
            'x' : x,
            'y': y,
            'dir': dir,
            'door_x': door_x,
            'door_y': door_y,
            'out_id': out_id
            }


    def door_sills(self, room):
        """ along the perimeter of the room, check for doorsills,
            return a list of possible doorsills
        """
        l = []
        if (room[NORTH] >= 3):
            for x in range(room[WEST], room[EAST] + 1, 2):
                proto = self.check_sill(room, x, room[NORTH], NORTH)
                if proto:
                    l += [proto]
        if (room[SOUTH] <= self.height - 3):
            for x in range(room[WEST], room[EAST] + 1, 2):
                proto = self.check_sill(room, x, room[SOUTH], SOUTH)
                if proto:
                    l += [proto]
        if (room[WEST] >= 3):
            for y in range(room[NORTH], room[SOUTH] + 1, 2):
                proto = self.check_sill(room, room[WEST], y, WEST)
                if proto:
                    l += [proto]
        if (room[EAST] <= self.height - 3):
            for y in range(room[NORTH], room[SOUTH] + 1, 2):
                proto = self.check_sill(room, room[EAST], y, EAST)
                if proto:
                    l += [proto]
        numpy.random.shuffle(l)
        return l

    def possible_opens(self, room):
        room_h = ((room[SOUTH] - room[NORTH]) / 2) + 1
        room_w = ((room[EAST] - room[WEST]) / 2) + 1
        flumph = int(numpy.sqrt(room_h * room_w))
        return flumph + int(numpy.random.randint(0, flumph))

    def door_type(self):
        """ returns a random door type """
        # only doors atm
        return DOOR
        # throw dice to get the doortype
        i = numpy.random.randint(0, 110)
        if i < 15:
            return ARCH
        elif i < 60:
            return DOOR
        elif i < 75:
            return LOCKED
        elif i < 90:
            return TRAPPED
        elif i < 100:
            return SECRET
        else:
            return PORTC

    def open_room(self, room):

        l = self.door_sills(room)
        if not l:
            return
        n_opens = self.possible_opens(room)
        self.connect = {}
        for i in xrange(n_opens):
            found = False
            while not found and len(l) > 0:
                # eliminate sills until we find a good one.
                j = numpy.random.randint(0, len(l))
                sill = l[j]
                out_id = sill.get('out_id', None)
                l.remove(sill)
                if not sill:
                    continue
                door_cell = self.cells[sill['door_x'], sill['door_y']]
                if door_cell & DOORSPACE:
                    continue
                if out_id:
                    connect = ','.join(
                            (str(min(room['id'], out_id)),
                             str(max(room['id'], out_id))))
                    if self.connect.has_key(connect):
                        self.connect[connect] += 1
                        if self.connect[connect] >= room['door_treshhold'](self.connect[connect]):
                            continue # no more doors here.
                    else:
                        self.connect[connect] = 0
                else:
                    # do we add random doors to non out_ids?
                    continue
                found = True
            for k in xrange(3):
                x = sill['x'] + (DOORX[sill['dir']] * k)
                y = sill['y'] + (DOORY[sill['dir']] * k)
                self.cells[x, y] &= ~PERIMETER
                self.cells[x, y] |= ENTRANCE
            door = {'x': sill['x'],
                    'y': sill['y'],
                    'key': 'door',
                    'out_id': out_id,
                    }
            self.cells[door['x'], door['y']] |= self.door_type()

    def corridors(self):
        for i in range(1, self.cx):
            x = (i * 2) + 1
            for j in range(1, self.cy):
                y = (j * 2) + 1
                if self.cells[x, y] & CORRIDOR:
                    continue
                self.tunnel(i, j)

    def tunnel(self, i, j, last_dir=None):
        dirs = self.tunnel_dirs(last_dir)
        for dir in dirs:
            if (self.open_tunnel(i, j, dir)):
                next_i = i + DOORX[dir]
                next_j = j + DOORY[dir]
                self.tunnel(next_i, next_j, dir)

    def tunnel_dirs(self, last_dir=None):
        p = CORRIDOR_LAYOUTS[self.opts.get('corridor_layout', 'straight')]
        dirs = DOORX.keys()
        numpy.random.shuffle(dirs)

        if last_dir and p:
            if numpy.random.randint(100) < p:
                dirs = [last_dir] + dirs
        return dirs

    def open_tunnel(self, i, j, dir):
        x = (i * 2) + 1
        y = (j * 2) + 1
        next_x = ((i + DOORX[dir]) * 2) + 1
        next_y = ((j + DOORY[dir]) * 2) + 1
        mid_x = (x + next_x) / 2
        mid_y = (y + next_y) / 2
        if self.sound_tunnel(mid_x, mid_y, next_x, next_y):
            return self.delve_tunnel(x, y, next_x, next_y)
        else:
            return False

    def sound_tunnel(self, mid_x, mid_y, next_x, next_y):
        if next_x < 0 or next_x > self.width or next_y < 0 or next_y > self.height:
            return False
        x1, x2 = sort(mid_x, next_x)
        y1, y2 = sort(mid_y, next_y)
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                if self.cells[x, y] & BLOCK_CORR:
                    return False
        return True

    def delve_tunnel(self, x, y, next_x, next_y):
        x1, x2 = sort(x, next_x)
        y1, y2 = sort(y, next_y)
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                self.cells[x, y] &= ~ENTRANCE
                self.cells[x, y] |= CORRIDOR
        return True

    def clean_dungeon(self):
        if self.opts.get('remove_deadends', False):
            self.remove_deadends()
        self.fix_doors()
        self.empty_blocks()

    def remove_deadends(self):
        return self.collapse_tunnels(self.opts['remove_deadends'],
                                     CLOSE_ENDS)

    def collapse_tunnels(self, p, xc):
        if not p:
            return
        for i in xrange(self.cx):
            x = (i * 2) + 1
            for j in xrange(self.cy):
                y = (j * 2) + 1
                if not self.cells[x, y] & OPENSPACE:
                    continue
                if self.cells[x, y] & STAIRS:
                    continue
                if not (p == 100 or int(numpy.random.randint(0, 100) < p)):
                    continue
                self.collapse(x, y, xc)

    def collapse(self, x, y, xc):
        try:
            if not self.cells[x, y] & OPENSPACE:
                return
        except IndexError:
            return

        for dir in xc.keys():
            if self.check_tunnel(x, y, xc[dir]):
                for p in xc[dir].get('close', []):
                    self.cells[x + p[1], y + p[0]] = NOTHING
                p = xc[dir].get('open', None)
                if p:
                    self.cells[x + p[1], y + p[0]] |= CORRIDOR
                p = xc[dir].get('recurse', None)
                if p:
                    self.collapse(x + p[1], y + p[0], xc)

    def check_tunnel(self, x, y, check):
        l = check.get('corridor', None)
        if l:
            for p in l:
                try:
                    if self.cells[x + p[1], y + p[0]] == CORRIDOR:
                        return False
                except IndexError:
                    pass
        l = check.get('walled', None)
        if l:
            for p in l:
                try:
                    if self.cells[x + p[1], y + p[0]] & OPENSPACE:
                        return False
                except IndexError:
                    pass
        return True

    def fix_doors(self):
        pass

    def empty_blocks(self):
        pass





def main():
    dungeon = Dungeon('Arcane Sanctum', 50, 50,
                      min_rooms=8,
                      max_rooms=12,
                      dungeon_layout='crest',
                      anything='possible',
                      )
    dungeon.init_cells()
    dungeon.emplace_rooms()
    dungeon.open_rooms()
    dungeon.corridors()
    dungeon.clean_dungeon()
    dungeon.ascii_output()

if __name__ == '__main__':
    main()

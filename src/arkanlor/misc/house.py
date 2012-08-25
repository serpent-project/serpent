
import numpy
from const import *

MAX_WIDTH = 30
MAX_HEIGHT = 30
LAYER_HEIGHT_BASE = 5
LAYER_HEIGHT_WALL = 20

class ccolors:
    CLEAR = '\033[0;0m'
    BOLD = '\033[1m'
    # fg
    BLACK = '\033[0;%im' % 30
    RED = '\033[0;%im' % 31
    GREEN = '\033[0;%im' % 32
    BROWN = '\033[0;%im' % 33
    BLUE = '\033[0;%im' % 34
    PURPLE = '\033[0;%im' % 35
    CYAN = '\033[0;%im' % 36
    LIGHT_GRAY = '\033[0;%im' % 37
    # light
    GRAY = '\033[1;%im' % 30
    PINK = '\033[1;%im' % 31
    LIGHT_GREEN = '\033[1;%im' % 32
    YELLOW = '\033[1;%im' % 33
    LIGHT_BLUE = '\033[1;%im' % 34
    MAGENTA = '\033[1;%im' % 35
    LIGHT_CYAN = '\033[1;%im' % 36
    WHITE = '\033[1;%im' % 37



class Room:
    def __init__(self, width=None, height=None, layer=0, room_id=0):
        self.room_id = room_id << 6
        self.width = width or numpy.random.randint(3, MAX_WIDTH)
        self.height = height or numpy.random.randint(3, MAX_HEIGHT)
        self.layer = layer or 0
        self.layer_height = LAYER_HEIGHT_WALL
        self.matrix = numpy.empty((self.width, self.height), dtype=int)
        self.matrix.fill(ROOM | self.room_id) # set all as room.

    def ascii_out(self):
        last_color = ccolors.CLEAR
        for y in xrange(self.height):
            line = ''
            for x in xrange(self.width):
                c = self.matrix[x, y]
                ch = '?'
                color = ccolors.CLEAR
                if c == NOTHING:
                    ch = 'o'
                if c & BLOCKED:
                    ch = 'x'
                if c & ROOM:
                    color = ccolors.YELLOW
                    ch = '='
                if c & CORRIDOR:
                    ch = '~'
                if c & PERIMETER:
                    color = ccolors.BROWN
                    ch = '+'
                if c & ENTRANCE:
                    ch = 'e'
                if c & DOORSPACE:
                    ch = 'd'
                # color handling
                if not last_color == color:
                    line += color
                    last_color = color
                line += ch
            print line
        print ccolors.CLEAR

    def raise_walls(self):
        for x in xrange(self.width):
            for y in xrange(self.height):
                self.matrix[x, 0] |= PERIMETER
                self.matrix[x, self.height - 1] |= PERIMETER
                self.matrix[0, y] |= PERIMETER
                self.matrix[self.width - 1, y] |= PERIMETER

    def create_doors(self, doornum=1):
        for i in xrange(doornum):
            # x or y?
            in_x = i + numpy.random.randint(0, 1) % 2
            at_max = i + 1 - numpy.random.randint(0, 1) % 2
            if in_xy: # in x
                y = 0 if not at_max else self.height - 1

            else:
                x = 0 if not at_max else self.width - 1


if __name__ == '__main__':
    room = Room(10, 10)
    room.raise_walls()
    room.ascii_out()

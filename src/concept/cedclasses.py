# -*- coding: utf-8 -*-
from OpenGL import GLU
from OpenGL.GL import *
import math, random#@UnresolvedImport
import vectorial

CELL_ALT = 0
CELL_TEX = 1
BOX_SIZE = 22
class Landscape(object):
    def __init__(self, width=None, height=None):
        if width is None and height is None:
            self.random_cells(100, 100)
        else:
            self.width = width
            self.height = height
            self.cells = [
                [
                [0, 0] for j in xrange(width)
                ] for i in xrange(height) ]
        self.cell_width = 0
        self.cell_height = 0

    def random_cells(self, width, height):
        """ generates random cells by width, height
        altitudes are set between -10 and +10
        textures are set between 0 and 5.
        """
        self.width = width
        self.height = height
        self.cells = [
                [
                [random.randint(0, 3),
                 random.randint(0, 0)] for j in xrange(height)
                ] for i in xrange(width) ]

    def get_normals_plain(self, x, y):
        cell = self.get_cell(x, y)
        ret = []
        if cell is not None:
            north, west, south, east = self.get_cell_nwse(x, y)
        else:
            north, west, south, east = 0, 0, 0, 0
        if (north == west) and (west == east) and (north == south):
            # actually it calls result[x].init( 0, 0, 1 )
            ret = [ [0, 0, 1] for x in xrange(4) ]
        else:
            ret.append(vectorial.normalize(
                       vectorial.cross(
                        [-BOX_SIZE, BOX_SIZE, (north - east) * 4],
                        [-BOX_SIZE, -BOX_SIZE, (west - north) * 4])))
            ret.append(vectorial.normalize(
                       vectorial.cross(
                        [BOX_SIZE, BOX_SIZE, (east - south) * 4],
                        [-BOX_SIZE, BOX_SIZE, (north - east) * 4])))
            ret.append(vectorial.normalize(
                       vectorial.cross(
                        [BOX_SIZE, -BOX_SIZE, (south - west) * 4],
                        [BOX_SIZE, BOX_SIZE, (east - south) * 4])))
            ret.append(vectorial.normalize(
                       vectorial.cross(
                        [BOX_SIZE, BOX_SIZE, (west - north) * 4],
                        [-BOX_SIZE, BOX_SIZE, (south - west) * 4])))
        return ret

    def get_normals(self, x, y):
        """
            returns a the normals for x,y
        """
        cells = []
        normals = []
        for i in [0, 1, 2]:
            inner_cells = []
            for j in [0, 1, 2]:
                inner_cells.append(self.get_normals_plain(x - 1 + i, y - 1 + j))
            cells.append(inner_cells)
        # this matrix represents:
        # normalization 1-4 of n'th element of i,j
        for m in [ [ [2, 0, 0], [1, 0, 1], [3, 1, 0], [0, 1, 1], ],
                   [ [2, 1, 0], [1, 1, 1], [3, 2, 0], [0, 2, 1], ],
                   [ [2, 1, 1], [1, 1, 2], [3, 2, 1], [0, 2, 2], ],
                   [ [2, 0, 1], [1, 0, 2], [3, 1, 1], [0, 1, 2], ],
                  ]:
            v = [0.0, 0.0, 0.0]
            for n, i, j in m:
                # here we actually use the matrix:
                v = vectorial.add(v, cells[i][j][n])
            normals.append(vectorial.normalize(v))
        return normals

    def get_mapblock(self, x, y):
        return None

    def get_cell(self, x, y):
        if x > self.width or x < 0 or y > self.height or y < 0:
            return None
        try:
            return self.cells[x][y]
        except:
            print "%s %s" % (x, y)
            raise

    def get_cell_nwse(self, x, y):
        """
            returns a 4 touple containing north, west, south, east
        """
        north = self.get_cell_alt(x, y, 0)
        west = self.get_cell_alt(x, y + 1, north)
        south = self.get_cell_alt(x + 1, y + 1, north)
        east = self.get_cell_alt(x + 1, y, north)
        return (north, west, south, east)

    def get_effective_altitude(self, x, y):
        """
        """
        north, west, east, south = self.get_cell_nwse(x, y)
        if abs(north - south) >= abs(west - east):
            return min(north, south) + abs(west - east) / 2
        else:
            return min(north, south) + abs(north - south) / 2

    def get_cell_alt(self, x, y, default=0):
        """ gets altitude of cell xy or default """
        cell = self.get_cell(x, y)
        if cell is not None:
            return cell[CELL_ALT]
        return default


def draw_quads_texture(x, y, neighbours,
                       focal_x, focal_y):
    y = y - 10
    x = x - 5
    drawx = 800 / 2 + (x - y) * BOX_SIZE
    drawy = 600 / 2 + (x + y) * BOX_SIZE
    north, west, south, east = neighbours
    return [ [drawx, drawy - north * 4],
             [drawx + BOX_SIZE, drawy + BOX_SIZE - east * 4],
             [drawx, drawy + BOX_SIZE * 2 - south * 4],
             [drawx - BOX_SIZE, drawy + BOX_SIZE - west * 4]
            ]


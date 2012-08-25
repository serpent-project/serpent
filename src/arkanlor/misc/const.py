# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Bitmask for generating different matrices for procedural generation.

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

DIR_A = 0x00100000
DIR_B = 0x00200000
CORNER = 0x00400000 # acts as 45° switch.
BLOCK = 0x00800000 # do not confuse with blocked.
CROSS = CORNER | BLOCK # means that all around same type.

# "ensw" check
EAST = DIR_A | DIR_B
NORTH = DIR_A
SOUTH = DIR_B
WEST = 0x0

# rot dir check
SOUTH_EAST = EAST | CORNER
NORTH_EAST = NORTH | CORNER
SOUTH_WEST = SOUTH | CORNER
NORTH_WEST = WEST | CORNER
# strangly this is true now: :D
DIR_XPOS = NORTH
DIR_YPOS = SOUTH

SUB_ID = 0xFF000000

OPENSPACE = ROOM | CORRIDOR
DOORSPACE = ARCH | DOOR
ESPACE = ENTRANCE | DOORSPACE | 0xFF000000

BLOCK_ROOM = BLOCKED | ROOM
BLOCK_CORR = BLOCKED | PERIMETER | CORRIDOR
BLOCK_DOOR = BLOCKED | DOORSPACE

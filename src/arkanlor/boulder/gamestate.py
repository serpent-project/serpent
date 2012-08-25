# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    GameState

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
from arkanlor.misc import dungeon
import numpy

class WorldObject(object):
    __slots__ = ['_id', 'name', '_var']
    def __init__(self, _id):
        self._id = _id
        self.name = None
        self._var = {}

    id = property(lambda x: x._id)


    def fill_dict(self, d, keys=[]):
        for key in keys:
            if self.hasattr(key):
                d[key] = self.getattr(key)
            elif key in self._var.keys():
                d[key] = self._var[key]
        #return d

class Mobile(WorldObject):
    __slots__ = WorldObject.__slots__ + ['hp', 'maxhp', 'body',
                                         'str', 'dex', 'int',
                                         'stam', 'maxstam',
                                         'mana', 'maxmana',
                                         'ar',
                                         'x', 'y', 'z', 'zhigh',
                                         'dir', 'color',
                                         ]
    def __init__(self, _id, x=None, y=None, z=None):
        super(Mobile, self).__init__(_id)
        self.hp = None
        self.maxhp = None
        self.body = None
        self.str = None
        self.dex = None
        self.int = None
        self.stam = None
        self.maxstam = None
        self.mana = None
        self.maxmana = None
        self.ar = 0
        self.color = 0
        self.dir = 0
        self.x = x or 0
        self.y = y or 0
        self.z = z or 0

class Item(WorldObject):
    __slots__ = WorldObject.__slots__ + ['graphic',
                                         'x', 'y', 'z', 'zhigh',
                                         'dir',
                                         'color', 'amount',
                                         ]
    def __init__(self, _id, x=None, y=None, z=None,
                 graphic=None):
        super(Item, self).__init__(_id)
        self.color = 0
        self.dir = 0
        self.x = x or 0
        self.y = y or 0
        self.z = z or 0
        self.graphic = graphic or 0x1 # nodraw
        self.amount = 1

    def packet_info(self):
        return {'color': self.color,
                'dir': self.dir,
                'x': self.x,
                'y': self.y,
                'z': self.z,
                'graphic': self.graphic,
                'amount': self.amount,
                'amount2': self.amount,
                }

class ItemMulti(Item):
    __slots__ = Item.__slots__ + [ 'items' ]

    def __init__(self, _id, x=None, y=None, z=None,
                 graphic=None,
                 items=None):
        super(ItemMulti, self).__init__(_id)
        self.color = 0
        self.dir = 0
        self.x = x or 0
        self.y = y or 0
        self.z = z or 0
        self.graphic = graphic or 0x2000
        self.amount = 1
        self.items = items or []

    def packet_info(self):
        return {'color': self.color,
                'dir': self.dir,
                'x': self.x,
                'y': self.y,
                'z': self.z,
                'graphic': self.graphic,
                'amount': self.amount,
                'amount2': self.amount,
                # multi data:
                'datatype': 0x02,
                }

    def add_item(self, x, y, z, graphic):
        self.items += [ {'x': x, 'y': y, 'z': z, 'graphic': graphic} ]


class Account(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password or ''



class BoulderState(object):
    def __init__(self, name):
        self.name = name
        self.mobiles = []
        self.items = []
        self.ids = {}
        self.free_id = 0x0222

    def get_next_free_id(self):
        """
            reserves a serial to be used.
        """
        id = self.free_id
        while id in self.ids.keys():
            id += 1
        self.ids[id] = None
        self.free_id = id + 1
        return id

    def get_object(self, id):
        try:
            return self.ids[id]
        except IndexError:
            return None

    def create_dungeon_in_area(self, cx, cy, cz, w, h):
        # temporary function to create a dungeon and send back an object list.
        # should mimic everything there is to object lists
        d = dungeon.Dungeon('Arcane Sanctum', w, h,
                      min_rooms=8,
                      max_rooms=12,
                      dungeon_layout='crest',
                      anything='possible',
                      )
        i = ItemMulti(self.get_next_free_id(),
                      cx, cy, cz)
        for x in xrange(d.width):
            for y in xrange(d.height):
                # 0x515: cobblestones.
                # 0x519: paved stones
                # 0x1771 + 11: stones
                # 0x0750: stone bricks
                graphic = None
                c = d.cells[x, y]
                if c == dungeon.NOTHING:
                    graphic = numpy.random.randint(0x1771, 0x1771 + 11)
                if c & dungeon.BLOCKED:
                    pass
                if c & dungeon.ROOM:
                    graphic = 0x519
                if c & dungeon.CORRIDOR:
                    graphic = 0x515
                if c & dungeon.PERIMETER:
                    graphic = 0x0750
                if c & dungeon.ENTRANCE:
                    pass
                if c & dungeon.DOORSPACE:
                    pass

                if graphic:
                    # create our item.
                    # o = Item(self.get_next_free_id(), x1 + x, y1 + y, 0, graphic)
                    i.add_item(x, y, 0, graphic)
        return i


    def gm_body(self, charname='GM Body', x=None, y=None, z=None):
        # create a mobile in our world as dragon
        mobile = Mobile(self.get_next_free_id(), x, y, z)
        mobile.name = charname
        mobile.hp, mobile.maxhp = 100, 100
        mobile.str, mobile.dex, mobile.int = 100, 100, 100
        mobile.stam, mobile.maxstam = 1000, 1000
        mobile.mana, mobile.maxmana = 9999, 9999
        mobile.ar = 10 # dragon scales! :D

        mobile.body = 0x190

        self.ids[mobile.id] = mobile
        self.mobiles += [mobile]
        return mobile






# -*- coding: utf-8 -*-
"""
    Dynamic Object Models.
    For data which is made without db interaction
"""


class Account(object):
    #@deprecated: well, this is obviously just temporary.
    def __init__(self, username, password):
        self.username = username
        self.password = password or ''


class MapObject(object):
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

class Mobile(MapObject):
    __slots__ = MapObject.__slots__ + ['hp', 'maxhp', 'body',
                                         'str', 'dex', 'int',
                                         'stam', 'maxstam',
                                         'mana', 'maxmana',
                                         'ar',
                                         'x', 'y', 'z', 'zhigh',
                                         'dir', 'color',
                                         'last_pos'
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
        self.remember_last_pos()

    def range_to_last_pos(self):
        # tell me how far am i from my last pos?
        return abs(self.last_pos[0] - self.x) + \
            abs(self.last_pos[1] - self.y)
    def remember_last_pos(self):
        self.last_pos = (self.x, self.y, self.z)

    def packet_info(self):
        return {
                'x': self.x,
                'y': self.y,
                'z': self.z,
                'body': self.body,
                'dir': self.dir,
                'color': self.color
                }



class Item(MapObject):
    __slots__ = MapObject.__slots__ + ['graphic',
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


# -*- coding: utf-8 -*-
"""
    Dynamic Object Models.
    For data which is made without db interaction
"""
from arkanlor.utils import between, sort

class Subscriptions(object):
    __slots__ = ['parent', 'clients']
    def __init__(self, parent):
        self.parent = parent
        self.clients = {}

    def subscribe(self, client):
        l = len(self.clients)
        self.clients[client.id] = client
        return len(self.clients) > l

    def unsubscribe(self, client):
        if client.id in self.clients.keys():
            del self.clients[client.id]

    def mobiles(self, client):
        ret = []
        for key, value in self.clients.items():
            if isinstance(value, Mobile):
                ret += [value]
        return ret

class WorldObject(object):
    __slots__ = ['_id', 'name', '_var', '_db', 'world']
    def __init__(self, world, _id):
        self._id = _id
        self.name = None
        self._var = {}
        self._db = None
        self.world = world

    id = property(lambda x: x._id)

    def position(self):
        return (self.x, self.y, self.z)

    def fill_dict(self, d, keys=[]):
        for key in keys:
            if self.hasattr(key):
                d[key] = self.getattr(key)
            elif key in self._var.keys():
                d[key] = self._var[key]
        #return d

class MapObject(WorldObject):
    """
        a map object defining a position in the world
    """
    __slots__ = WorldObject.__slots__ + ['x', 'y', 'z', 'map']
    def __init__(self, world, _id, x=None, y=None, z=None,):
        super(MapObject, self).__init__(world, _id)
        self.x = x or 0
        self.y = y or 0
        self.z = z or 0


class Mobile(MapObject):
    __slots__ = MapObject.__slots__ + [  'subscribers',
                                         'hp', 'maxhp', 'body',
                                         'str', 'dex', 'int',
                                         'stam', 'maxstam',
                                         'mana', 'maxmana',
                                         'ar',
                                         'zhigh',
                                         'dir', 'color',
                                         'last_pos'
                                         ]
    def __init__(self, world, _id, x=None, y=None, z=None):
        super(Mobile, self).__init__(world, _id, x, y, z)
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
        self.subscribers = None
        self.remember_last_pos()

    def _db_create(self, DBModel):
        self._db = DBModel()
        self._db_update()
        self._id = self._db.id
        return self._db

    def _db_sync(self, source, target):
        target.name = source.name
        target.x = source.x
        target.y = source.y
        target.z = source.z
        target.hp = source.hp
        target.maxhp = source.maxhp
        target.body = source.body
        target.str = source.str
        target.dex = source.dex
        target.int = source.int
        target.stam = source.stam
        target.maxstam = source.maxstam
        target.mana = source.mana
        target.maxmana = source.maxmana
        target.ar = source.ar
        target.color = source.color
        target.dir = source.dir

    def _db_update(self):
        self._db_sync(self, self._db)
        return self._db.save()

    def _db_read(self):
        self._db_sync(self._db, self)
        self._id = self._db.id

    def subscribe(self, client):
        if self.subscribers is None:
            self.subscribers = Subscriptions(self)
        return self.subscribers.subscribe(client)

    def appear_to(self, client):
        self.world.create_mobile_for_mobile(self, client)

    def update_to(self, client):
        self.world.update_mobile_for_mobile(self, client)

    def disappear_to(self, client):
        self.world.remove_mobile_for_mobile(self, client)

    def update_subscribers(self):
        for mobile in self.world.get_mobiles_near_mobile(self):
            if mobile.subscribe(self):
                # i am new.
                self.appear_to(mobile)
            else:
                self.update_to(mobile)
        # todo: unsubscribe!

    def walk(self, dir=None):
        if dir is None:
            dir = self.dir
        pos = self.position()
        retcode, mob = self.world.try_move(self, dir)
        # if i could not move return false.
        if retcode:
            return False
        # update the world in front of me
        self.update_subscribers()
        return True

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
                                         'zhigh',
                                         'dir',
                                         'color', 'amount',
                                         ]
    def __init__(self, world, _id, x=None, y=None, z=None,
                 graphic=None):
        super(Item, self).__init__(world, _id, x, y, z)
        self.color = 0
        self.dir = 0
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

    def __init__(self, world, _id, x=None, y=None, z=None,
                 graphic=None,
                 items=None):
        super(ItemMulti, self).__init__(world, _id, x, y, z)
        self.color = 0
        self.dir = 0
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


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

class WorldObject(object):
    __slots__ = ['serial', 'name', '_var']
    def __init__(self, serial):
        self.serial = serial
        self.name = None
        self._var = {}


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
    def __init__(self, serial, x=None, y=None, z=None):
        super(Mobile, self).__init__(serial)
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

class Account(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password or ''



class BoulderState(object):
    def __init__(self, name):
        self.name = name
        self.mobiles = []
        self.items = []
        self.serials = {}
        self.free_serial = 0x0222

    def get_next_free_serial(self):
        """
            reserves a serial to be used.
        """
        serial = self.free_serial
        while serial in self.serials.keys():
            serial += 1
        self.serials[serial] = None
        self.free_serial = serial + 1
        return serial

    def gm_body(self, charname='GM Body', x=None, y=None, z=None):
        # create a mobile in our world as dragon
        mobile = Mobile(self.get_next_free_serial(), x, y, z)
        mobile.name = charname
        mobile.hp, mobile.maxhp = 100, 100
        mobile.str, mobile.dex, mobile.int = 100, 100, 100
        mobile.stam, mobile.maxstam = 1000, 1000
        mobile.mana, mobile.maxmana = 9999, 9999
        mobile.ar = 10 # dragon scales! :D

        mobile.body = 0x3C

        self.serials[mobile.serial] = mobile
        self.mobiles += [mobile]
        return mobile






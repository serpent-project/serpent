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
import models, dynamic
import numpy

DIR_N = 0x00
DIR_NE = 0x01
DIR_E = 0x02
DIR_SE = 0x03
DIR_S = 0x04
DIR_SW = 0x05
DIR_W = 0x06
DIR_NW = 0x07
DIR_RUNNING = 0x80
DIR_MASK = 0x07

DIR_MATRIX = {
        DIR_N: [0, -1],
        DIR_NE: [1, -1],
        DIR_E: [1, 0],
        DIR_SE: [1, 1],
        DIR_S: [0, 1],
        DIR_SW: [-1, 1],
        DIR_W: [-1, 0],
        DIR_NW: [-1, -1],
        }

class BoulderState(object):
    def __init__(self, name):
        self.name = name
        self.mobiles = []
        self.items = []
        self.ids = {}
        self.free_id = 0x0222
        self.worldmap = models.WorldMap.objects.get(name='default')


    def get_next_free_id(self):
        """
            reserves a serial to be used.
            note: database <> dynamic id handling to be solved
            for now, all efforts go into direct db solution.
        """
        id = self.free_id
        while id in self.ids.keys():
            id += 1
        self.ids[id] = None
        self.free_id = id + 1
        return id

    def get_object(self, id):
        # seek in db
        try:
            return models.Item.objects.get(worldmap=self.worldmap,
                                           id=id)
        except models.Item.DoesNotExist, e:
            try:
                return self.ids[id]
            except IndexError:
                return None

    def items_in_rect(self, x1, y1, x2, y2):
        # request all items in a rectangle
        # db method
        items = models.Item.objects.filter(
                                    worldmap=self.worldmap,
                                    x__gte=x1,
                                    x__lt=x2,
                                    y__gte=y1,
                                    y__lt=y2)
        return items

    def items_outer_rect(self, x, y, dx=32, dy=32, minimal=8):
        items = models.Item.objects.filter(
                                    worldmap=self.worldmap,
                                    x__gte=x - dx,
                                    x__lt=x + dx,
                                    y__gte=y - dx,
                                    y__lt=y + dx,
                                    ).exclude(
                                    x__gte=x - dx + minimal,
                                    x__lt=x + dx - minimal,
                                    y__gte=y - dx + minimal,
                                    y__lt=y + dx - minimal,
                                    )
        return items

    def mobiles_in_rect(self, x1, y1, x2, y2):
        mobs = []
        for mobile in self.mobiles:
            if (mobile.x >= x1) and (mobile.x < x2) and (mobile.y >= y1) and (mobile.y < y2):
                mobs += [mobile]
        return mobs

    def gm_body(self, charname='GM Body', x=None, y=None, z=None):
        # create a mobile in our world as dragon
        mobile = dynamic.Mobile(self.get_next_free_id(), x, y, z)
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

    def try_move(self, mobile, direction):
        """
            tries to move a mobile.
            returns (returncode, mobile)
            returncode means:
                - 0 walking ok
                - 1 walking denied
                - 2 walking denied + resync.
        """
        if mobile.dir & DIR_MASK != direction & DIR_MASK:
            mobile.dir = direction
            #if not direction & DIR_RUNNING:
            return 0, mobile
        dx, dy = DIR_MATRIX[direction & DIR_MASK]
        nx, ny = mobile.x + dx, mobile.y + dy
        # check walk here
        mobile.x, mobile.y = nx, ny
        mobile.dir = direction
        return 0, mobile



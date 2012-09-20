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
import models, dynamics
import numpy
from arkanlor.boulder.map import UOMap, Map
from arkanlor.boulder.generators.landscape import BiomeMap
from django.conf import settings
from arkanlor.boulder.generators.continents import UOContinent
from arkanlor.boulder.generators.dragonmap import SimpleDragonContinent
from arkanlor.boulder.generators.old.example import ExampleContinent
from arkanlor.boulder.generators.grassland import EndlessGrass

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
    def __init__(self, name, task=None):
        self.task = task # the boulder task, commonly referred to as "_world".
        self.name = name # a name
        self.mobiles = []
        self.items = []
        self.ids = {}
        self.free_id = 0x0222
        self.worldmap_db = models.WorldMap.objects.get(name='default')
        self.worldmap = BiomeMap(self, size=settings.DEFAULT_MAP0_SIZE)
        # if one of these fails, simply comment them out.
        # these will be removed later, if boulder evolves.
        self.worldmap.continents.register_continent(ExampleContinent((16, 16), 10, 1))
        self.worldmap.continents.register_continent(EndlessGrass((25, 25), 15, 10))
        self.worldmap.continents.register_continent(SimpleDragonContinent((8, 8), 1, 1))
        self.worldmap.continents.register_continent(
                                        UOContinent(
                                            (128, 128),
                                            1, 16,
                                            mapmul=settings.DEFAULT_MAP0,
                                            map_offset_bx=15,
                                            map_offset_by=480,
                                                    )
                                                    )

    def get_map(self):
        return self.worldmap

    def get_map_db(self):
        return self.worldmap_db

    def create_mobile_for_mobile(self, mobile, client):
        """
            * sends appropriate script signal
            * if mobile is an agent, he is notified via packets. 
        """
        if isinstance(client, dynamics.Agent) and client.socket:
            client.socket.send_object(mobile)

    def update_mobile_for_mobile(self, mobile, client):
        """
            * sends appropriate script signal
            * if mobile is an agent, he is notified via packets.
        """
        if isinstance(client, dynamics.Agent) and client.socket:
            client.socket.send_object(mobile, update_only=True)

    def remove_mobile_for_mobile(self, mobile, client):
        """
            * sends appropriate script signal
            * if mobile is an agent, he is notified via packets
        """
        pass

    def get_mobiles_near_mobile(self, client):
        """
            return a list of mobiles near this mobile.
        """
        mobs = []
        x1, y1 = client.x - 18, client.y - 18
        x2, y2 = client.x + 18, client.y + 18
        for mobile in self.mobiles:
            if (mobile != client)\
            and (mobile.x >= x1) and (mobile.x < x2)\
            and (mobile.y >= y1) and (mobile.y < y2):
                mobs += [mobile]
        return mobs

    def get_next_free_id(self):
        """
            reserves a serial to be used.
            note: database <> dynamic id handling to be solved
            for now, all efforts go into direct db solution.
            @deprecated: try to rely on db based stuff.
        """
        id = self.free_id
        while id in self.ids.keys():
            id += 1
        #self.ids[id] = None
        #self.free_id = id + 1
        return id

    def get_object(self, id):
        # seek in db
        try:
            return models.Item.objects.get(worldmap=self.worldmap_db,
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
                                    worldmap=self.worldmap_db,
                                    x__gte=x1,
                                    x__lt=x2,
                                    y__gte=y1,
                                    y__lt=y2)
        return items

    def items_outer_rect(self, x, y, dx=18, dy=18, minimal=8):
        items = models.Item.objects.filter(
                                    worldmap=self.worldmap_db,
                                    x__gte=x - dx,
                                    x__lt=x + dx,
                                    y__gte=y - dy,
                                    y__lt=y + dy,
                                    ).exclude(
                                    x__gte=x - dx + minimal,
                                    x__lt=x + dx - minimal,
                                    y__gte=y - dy + minimal,
                                    y__lt=y + dy - minimal,
                                    )
        return items

    def mobiles_in_rect(self, x1, y1, x2, y2):
        mobs = []
        for mobile in self.mobiles:
            if (mobile.x >= x1) and (mobile.x < x2) and (mobile.y >= y1) and (mobile.y < y2):
                mobs += [mobile]
        return mobs

    def new_body(self, mobile_type=None,
                       name='Man',
                       x=None, y=None, z=None,
                       socket=None,
                       dont_persist=False):
        if socket:
            mobile = dynamics.Agent(self,
                                    self.get_next_free_id(),
                                    x, y, z,
                                    socket)
        else:
            mobile = dynamics.Mobile(self,
                                    self.get_next_free_id(),
                                    x, y, z)
        mobile.name = name
        mobile.hp, mobile.maxhp = 100, 100
        mobile.str, mobile.dex, mobile.int = 100, 100, 100
        mobile.stam, mobile.maxstam = 100, 100
        mobile.mana, mobile.maxmana = 100, 100
        mobile.ar = 0 # dragon scales! :D
        mobile.body = 0x190
        if mobile_type:
            mobile._db_create(mobile_type)
        if not dont_persist:
            self.ids[mobile.id] = mobile
            self.mobiles += [mobile]
        return mobile

    def get_agent(self, db_instance, socket=None):
        if db_instance.id in self.ids.keys():
            mobile = self.ids[db_instance.id]
        else:
            mobile = dynamics.Agent(self, None, db_instance.x, db_instance.y, db_instance.z,)
            mobile._db = db_instance
            mobile._db_read()
            self.ids[db_instance.id] = mobile
            self.mobiles += [mobile]
        if socket:
            mobile.socket = socket
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

    def world_info(self):
        # get infos about this boulder
        return {
                'num_mobiles': len(self.mobiles),
                'num_items': models.Item.objects.filter(worldmap=self.worldmap_db).count(),
                }


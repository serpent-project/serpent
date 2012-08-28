# -*- coding: utf-8 -*-

"""
    This engine maintains control over an entry to the worldstate
    it retrieves data from the map
"""
from arkanlor.uos.engine import Engine#@UnresolvedImport
from arkanlor.uos import packets as p
from arkanlor.uos import const
from arkanlor import settings
from arkanlor.boulder import dynamic, models

class MapClient(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)
        self.serials = {}
        self.ids = {}
        self.serial_base = 0x1000

    def on_login(self, user, mobile):
        self.send(p.GIMapChange())
        # just save it for now?
        self.user = user
        self.mobile = mobile
        # send area around mobile.
        self.send_mobile_area(mobile)

    def send_mobile_area(self, mobile=None):
        if mobile is None:
            mobile = self.mobile
        items = self._ctrl._world.gamestate.items_in_rect(mobile.x - 10,
                                                         mobile.y - 10,
                                                         mobile.x + 10,
                                                         mobile.y + 10)
        for item in items:
            self.send_object(item)

    def send_object(self, obj):
        serial = None
        if obj.id in self.ids.keys():
            serial = self.serials[obj.id]
        else:
            serial = self.get_new_serial()
        if isinstance(obj, models.WorldObject):
            obj = obj.as_leaf()
        if isinstance(obj, models.ItemMulti) or isinstance(obj, dynamic.ItemMulti):
            # send multi data.

            # send multi item.
            pck = obj.packet_info()
            pck['serial'] = serial
            self.send(p.ObjectInfo(pck))
            self.send(p.ServerMulti({'serial': serial,
                                     'revision': serial,
                                     'items': obj.items}))
        elif isinstance(obj, models.Item) or isinstance(obj, dynamic.Item):
            pck = obj.packet_info()
            pck['serial'] = serial
            self.send(p.ObjectInfo(pck))
        if serial:
            # save our serial
            self.serials[serial] = obj.id

    def update_serials(self):
        # rebuild id cache
        ids = {}
        for key, value in self.serials.items():
            if value:
                ids[value] = key
        self.ids = ids

    def get_new_serial(self):
        return self.get_new_serials(1)[0]

    def get_new_serials(self, amount=1):
        l = []
        if amount:
            i = self.serial_base
            while len(l) < amount:
                if i not in self.serials.keys():
                    self.serials[i] = None
                    l += [i]
                i += 1
        return l

    def send_object_list(self, object_list):
        self.update_serials()
        packets = []
        for o in object_list:
            #if not o.id:
            #    continue
            # get our serial
            pass
        self.sendall(packets)

    def update_rect(self, x1, y1, x2, y2):
        # send all items in a rectangle.
        pass


    def on_packet(self, packet):
        pass

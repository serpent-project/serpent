# -*- coding: utf-8 -*-

"""
    This engine maintains control over an entry to the worldstate
    it retrieves data from the map
"""
from arkanlor.uos.engine import Engine#@UnresolvedImport
from arkanlor.uos import packets as p
from arkanlor.uos import const
from arkanlor import settings
from arkanlor.boulder import dynamics, models

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
        self.send_mobile_area(mobile, True)

    def send_mobile_area(self, mobile=None, full=False):
        if mobile is None:
            mobile = self.mobile
        if full:
            x1, y1 = mobile.x - 32, mobile.y - 32
            x2, y2 = mobile.x + 32, mobile.y + 32
            items = self._ctrl._world.gamestate.items_in_rect(x1, y1, x2, y2)
            mobiles = self._ctrl._world.gamestate.mobiles_in_rect(x1,
                                                              y1,
                                                              x2,
                                                              y2,)
        else:
            items = self._ctrl._world.gamestate.items_outer_rect(mobile.x, mobile.y)
            mobiles = []
        for item in items:
            self.send_object(item)

        for mobile in mobiles:
            if mobile != self.mobile:
                self.send_object(mobile)

    def get_serial(self, obj, notify=False):
        serial_new = False
        if obj.id in self.ids.keys():
            serial = self.ids[obj.id]
        else:
            serial_new = True
            serial = self.get_new_serial()
        if notify:
            return serial_new, serial
        return serial


    def send_object(self, obj, update_only=False):
        serial_new, serial = self.get_serial(obj, True)
        if isinstance(obj, models.WorldObject):
            obj = obj.as_leaf()
        if isinstance(obj, models.ItemMulti) or isinstance(obj, dynamics.ItemMulti):
            # send multi item.
            pck = obj.packet_info()
            pck['serial'] = serial
            self.send(p.ObjectInfo(pck))
            #if serial_new:
            self.send(p.ServerMulti({'serial': serial,
                                     'revision': serial,
                                     'items': obj.items}))
        elif isinstance(obj, models.Item) or isinstance(obj, dynamics.Item):
            pck = obj.packet_info()
            pck['serial'] = serial
            self.send(p.ObjectInfo(pck))
        elif isinstance(obj, dynamics.Mobile):
            pck = obj.packet_info()
            pck['serial'] = serial
            # create
            if not update_only or serial_new:
                self.send(p.ShowMobile(pck))
            else:
                self.send(p.UpdateMobile(pck))
            # todo: for new serials make sure name is sent.

        if serial:
            # save our serial
            self.serials[serial] = obj.id
            self.ids[obj.id] = serial


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

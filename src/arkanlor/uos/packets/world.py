# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Category World: data the world sends, like items, mobs, ...

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
from arkanlor.uos.packet_io import BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets
from arkanlor.uos.packet_io import UOPacket as Packet
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP

class ObjectOldInfo(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x1a
    p_type = P_SERVER
    _datagram = []
    # @todo: 

class ObjectInfo(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xf3
    p_type = P_SERVER
    p_size = 24
    _datagram = [
            ('info', USHORT, None, 0x1), # always 0x1 on OSI
            ('datatype', BYTE), # 0x00 item, 0x02 multi
            ('serial', UINT),
            ('graphic', USHORT),
            ('dir', BYTE),
            ('amount', USHORT),
            ('amount2', USHORT), # sent 2 times for unknown reason.
            ('x', USHORT),
            ('y', USHORT),
            ('z', BYTE),
            ('layer', BYTE),
            ('color', USHORT),
            ('flag', BYTE),
                 ]

class ServerMulti(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xd8
    p_size = 0
    p_type = P_SERVER
    _datagram = [
        ('compression', BYTE),
        ('unknown', BYTE),
        ('serial', UINT),
        ('revision', UINT),
        ('count', USHORT),
        ('bufferlength', USHORT),
        ('planecount', BYTE), # unsure if existant.
        ]

    def unpack(self):
        self.read_datagram(self._datagram)
        if self.values.get('compression', 0x0):
            # we do not do any compressions
            self.read_datagram([('compressed', RAW)])
            return self
        _multipart_datagram = [
                           ('graphic', USHORT),
                           ('x', BYTE),
                           ('y', BYTE),
                           ('z', BYTE)]
        self.values['items'] = []
        for x in xrange(self.values.get('count', 0)):
            item = {}
            self.read_datagram(_multipart_datagram, item)
            self.values['items'] += [item]
        return self

    def serialize(self):
        self.begin()
        num = len(self.values['items'])
        self.values['count'] = num
        self.values['buffersize'] = num * 5
        self.values['compression'] = 0x0
        self.write_datagram(self._datagram)
        items = self.values.get('items', [])
        _multipart_datagram = [
                           ('graphic', USHORT),
                           ('x', BYTE),
                           ('y', BYTE),
                           ('z', BYTE)]
        for x in xrange(num):
            self.write_datagram(_multipart_datagram, items[x])
        return self.finish()

class ShowMobile(Packet):
    """ also refered to as EquipMob """
    __slots__ = Packet.__slots__
    p_id = 0x78
    p_size = 0
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('body', USHORT),
            ('x', USHORT),
            ('y', USHORT),
            ('z', BYTE),
            ('dir', BYTE),
            ('color', USHORT),
            ('status', BYTE),
            ('notoriety', BYTE), ]

    def unpack(self):
        self.read_datagram(self._datagram)
        _equipped_item_datagram = [
                           ('serial', UINT),
                           ('graphic', USHORT),
                           ('layer', BYTE),
                           ('color', USHORT)]
        self.values['items'] = []
        while len(self._data) > 4:
            item = {}
            self.read_datagram(_equipped_item_datagram, item)
            self.values['items'] += [item]
        return self

    def serialize(self):
        self.begin()
        self.write_datagram(self._datagram)
        items = self.values.get('items', [])
        _equipped_item_datagram = [
                           ('serial', UINT),
                           ('graphic', USHORT),
                           ('layer', BYTE),
                           ('color', USHORT)]
        for x in xrange(len(items)):
            self.write_datagram(_equipped_item_datagram, items[x])
        self.w_uint(0) # terminator of loop
        return self.finish()

class ShowMobileExtended(ShowMobile):
    """ also refered to as Show Mobile, or EquipMOB Extended"""
    __slots__ = ShowMobile.__slots__
    p_id = 0xd3
    p_size = 0
    p_type = P_SERVER
    _datagram = ShowMobile._datagram + [
                    (0, USHORT),
                    (1, USHORT),
                    (2, USHORT),
                ]

class UpdateMobile(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x77
    p_size = 0x11
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('body', USHORT),
            ('x', USHORT),
            ('y', USHORT),
            ('z', BYTE),
            ('dir', BYTE),
            ('color', USHORT),
            ('status', BYTE),
            ('notoriety', BYTE),
            ]

class UpdateMobileExtended(UpdateMobile):
    __slots__ = Packet.__slots__
    p_id = 0x78
    p_size = 0x19
    p_type = P_SERVER
    _datagram = UpdateMobile._datagram + [
            (0, USHORT),
            (1, USHORT),
            (2, USHORT),
            (3, USHORT),
            ]


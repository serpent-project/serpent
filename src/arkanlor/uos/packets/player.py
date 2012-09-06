# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Packets handling movements, player data.

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
from arkanlor.dagrm import BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets
from arkanlor.uos.packet import UOPacket as Packet
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP


class MoveAck(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x22
    p_type = P_BOTH
    _datagram = [('seq', BYTE),
                 ('notoriety', BYTE)]

class MoveReject(Packet):
    """
        BYTE[1] sequence #
        BYTE[2] xLoc
        BYTE[2] yLoc
        BYTE[1] direction
        BYTE[1] zLoc
    """
    __slots__ = Packet.__slots__
    p_id = 0x23
    p_type = P_SERVER
    _datagram = [('seq', BYTE),
                 ('x', USHORT),
                 ('y', USHORT),
                 ('dir', BYTE),
                 ('z', BYTE)]


class MoveRequest(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x02
    p_type = P_CLIENT
    _datagram = [('dir', BYTE),
                 ('seq', BYTE),
                 ('fw_prev', UINT)]

    def __unicode__(self):
        return u'Movement with sequence %s in direction %s, fw_prev=%s' % (self.values.get('seq', '-'),
                                                                           hex(self.values.get('dir', 0x9)),
                                                                           self.values.get('fw_prev', '-'))
class UpdatePlayer(Packet):
    """
        http://docs.polserver.com/packets/index.php?Packet=0x77
    """
    __slots__ = Packet.__slots__
    p_id = 0x77
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('body', USHORT),
            ('x', USHORT), ('y', USHORT), ('z', BYTE),
            ('dir', BYTE),
            ('color', USHORT),
            ('flag', BYTE),
            ('highlight', BYTE)
            ]

class Teleport(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x20
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('body', USHORT),
            (0, BYTE),
            ('color', USHORT),
            ('flag', BYTE),
            ('x', USHORT), ('y', USHORT),
            (1, USHORT),
            ('dir', BYTE),
            ('z', BYTE),
            ]

class StatusBarInfo(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x11
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('name', FIXSTRING, 30),
            ('hp', USHORT),
            ('maxhp', USHORT),
            ('flag_namechange', BOOLEAN),
            ('flag_status', BYTE),

            ('racegender', BYTE),
            ('str', USHORT),
            ('dex', USHORT),
            ('int', USHORT),
            ('stam', USHORT),
            ('maxstam', USHORT),
            ('mana', USHORT),
            ('maxmana', USHORT),
            ('gold', UINT),
            ('ar', USHORT),
            ('weight', USHORT),
                 ]

    def extend_datagram(self):
        """
            status flag indicates an extended datagram
            0x01: T2A Extended Info, 
            0x03: UOR Extended Info, 
            0x04: AOS Extended Info (4.0+), 
            0x05: UOML Extended Info (5.0+), 
            0x06: UOKR Extended Info (UOKR+)
        """
        if self.values.get('flag_status', 0x0):
            status = self.values.get('flag_status', 0x0)
            if status >= 0x01:
                self._datagram += [ ('maxweight', USHORT),
                                    ('race', BYTE) ]
            if status >= 0x03:
                self._datagram += [ ('statscap', USHORT),
                                    ('followers', BYTE),
                                    ('maxfollowers', BYTE) ]
            if status >= 0x04:
                self._datagram += [ ('resist_fire', USHORT),
                                    ('resist_cold', BYTE),
                                    ('resist_poison', BYTE),
                                    ('resist_energy', BYTE),
                                    ('luck', BYTE),
                                    ('mindam', BYTE),
                                    ('maxdam', BYTE),
                                    ('titching_points', BYTE),
                                  ]



    def serialize(self):
        self.extend_datagram()
        return super(StatusBarInfo, self).serialize()

    #def unpack(self):
    #    self.extend_datagram()
    #    return super(StatusBarInfo, self).unpack()


class GetPlayerStatus(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x34
    p_type = P_CLIENT
    _datagram = [(0, UINT),
                 ('type', BYTE),
                 ('serial', UINT)]


class SingleClick(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x09
    _datagram = [('serial', UINT)]

    def __unicode__(self):
        return u'Clicked %s' % (self.values.get('serial', None))

class DoubleClick(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x06
    _datagram = [('serial', UINT)]

    def __unicode__(self):
        return u'DoubleClicked %s' % (self.values.get('serial', None))


class Follow(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x15
    p_type = P_BOTH

    _datagram = [('target', UINT), # to follow
                 ('serial', UINT)] # is following

class ResurrectionMenu(Packet):
    """
        action: 0 server, 1 resurrect, 2 ghost
    """
    __slots__ = Packet.__slots__
    p_id = 0x2c
    p_type = P_BOTH

    _datagram = [('action', BYTE)]

class RemoveGroup(Packet):
    """
        @deprecated: unneccessary.
        target = serial -> Removed from Group.
    """
    __slots__ = Packet.__slots__
    p_id = 0x39
    p_type = P_BOTH

    _datagram = [('serial', UINT),
                 ('target', UINT)]

class SendSkills(Packet):
    #@todo: not finished.
    __slots__ = Packet.__slots__
    p_id = 0x1c
    p_type = P_SERVER

    _datagram = [('type', BYTE)]

    def unpack(self):
        self.read_datagram(self._datagram)
        _skill_datagram = [('id', USHORT),
                           ('value', USHORT),
                           ('rawvalue', USHORT),
                           ('lock', BYTE)]
        if self.values['type'] in [0x02, 0xDF]:
            _skill_datagram += [('cap', USHORT)]
        self.values['skills'] = {}
        while len(self._data) > 2:
            skill = {}
            self.read_datagram(_skill_datagram, skill)
            self.values['skills'][skill['id']] = skill
        # skip the terminator.
        return self

    def serialize(self):
        self.begin()

        self.write_datagram(self._datagram)
        # @todo: writing dynamic packets cleanup
        return self.finish()

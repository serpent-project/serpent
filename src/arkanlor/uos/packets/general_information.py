# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    The General Information Packet.
    This packet has a lot of subpackets, so it deserves its own file.

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
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets, Packet
from arkanlor.uos.packet import UOPacket
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP

def AsGI(packet_type, values):
    values['subcmd'] = packet_type.p_id
    return GeneralInformation(values)

class GISubPacket(Packet):
    __slots__ = Packet.__slots__
    p_type = 0xbf
    def serialize(self):
        gi = AsGI(self, self.values)
        return gi.serialize()
    def read_data(self, length):
        if len(self._data) < length:
            return '\0' * length
        x, self._data = self._data[:length], self._data[length:]
        return x

class ScreenSize(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x05
    _datagram = [(0, USHORT),
                 ('x', USHORT),
                 ('y', USHORT),
                 (1, USHORT)]

class PartySystem(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x6
    _datagram = [('subsubcmd', BYTE), ]
    # @todo: manually read subsubcmd.

class MapChange(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x08
    _datagram = [('map', BYTE), ]

class ClientLanguage(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0xb
    _datagram = [('code', FIXSTRING, 3)]

class ClientType(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0xf
    _datagram = [(0, BYTE, None, 0x0a),
                 ('flag', UINT)
                 ]

    def __unicode__(self):
        return u'Client Type is %s' % hex(self.values.get('flag', 0))

class UOSEUnknown(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x24
    _datagram = [('se', BYTE)]

    def __unicode__(self):
        return u'UOSEUnknown is %s' % hex(self.values.get('se', 0))


class UnknownCliloc(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x10
    _datagram = [('serial', UINT),
                 ('command', UINT)]
    def __unicode__(self):
        return u'UnknownCliloc for serial %s with command %s' % (
                                        hex(self.values.get('serial', 0)),
                                        hex(self.values.get('command', 0)),
                                        )

class Client3DAction(GISubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x0e
    _datagram = [('anim', UINT)]

    def __unicode__(self):
        return u'Client 3d Action %s' % hex(self.values.get('anim', 0))

gi_subpackets = SubPackets('subcmd',
                             MapChange,
                             ClientLanguage,
                             ClientType,
                             Client3DAction,
                             UOSEUnknown,
                             UnknownCliloc,
                             PartySystem,
                             ScreenSize,
                             )

class GeneralInformation(UOPacket):
    """    
        Very complex all-in-one-packet.
    """
    __slots__ = Packet.__slots__
    p_id = 0xbf
    p_type = P_BOTH
    _datagram = [ ('subcmd', USHORT),
                  gi_subpackets ]

    def _unpack(self):
        # detect our type
        p_id = self.values.get('subcmd', None)
        if not p_id:
            return self
        p = gi_subpackets.packets.get(p_id, None)
        if not p:
            return self
        p = p(self.values)
        p._data = self._data
        return p



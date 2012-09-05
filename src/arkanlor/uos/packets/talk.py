# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    All about talking, commands, emoting, chat (?)

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
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets, UCSTRING
from arkanlor.uos.packet_io import UOPacket as Packet
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP

class TalkRequest(Packet):
    p_id = 0x03
    p_type = P_CLIENT
    _datagram = [
                ('ttype', BYTE),
                ('color', USHORT),
                ('font', USHORT),
                ('message', CSTRING)
                 ]
    def __unicode__(self):
        return u'Talk: <%s> %s' % (hex(self.values.get('ttype')),
                             self.values.get('message'),)

class UnicodeTalkRequest(Packet):
    p_id = 0xad
    p_type = P_CLIENT
    _datagram = [('ttype', BYTE),
                 ('color', USHORT),
                 ('font', USHORT),
                 ('lang', FIXSTRING, 3), # 4 bytes.
                 (0, BYTE), # terminator
                 ('message', UCSTRING)
                 ]
    # note this packet can be highly complex,
    # the condition is ttype & 0xc0 -> message gets a 12 bit list prepended.
    # first 12 bits: length of 12 bit list
    # then length * 12 bits -> keywords
    # (and +4 if number is even, to fill up the bytes)


#### Client Sent Packets
# these packets need packet parsing classes for the server.


#### Server Sent Packets
# these packets need to get packetwriters for the server.




class SendSpeech(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x1c
    p_type = P_SERVER

    _datagram = [('serial', UINT),
                 ('model', USHORT),
                 ('ttype', BYTE),
                 ('color', USHORT),
                 ('font', USHORT),
                 ('name', FIXSTRING, 30),
                 ('message', CSTRING)
                 ]

class SendUnicodeSpeech(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xae
    p_type = P_SERVER

    _datagram = [('serial', UINT),
                 ('model', USHORT),
                 ('ttype', BYTE),
                 ('color', USHORT),
                 ('font', USHORT),
                 ('lang', FIXSTRING, 3),
                 (0, BYTE), #terminator
                 ('name', FIXSTRING, 30),
                 ('message', UCSTRING)
                 ]

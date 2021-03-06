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
from arkanlor.dagrm import BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets, UCSTRING
from arkanlor.uos.packet import UOPacket as Packet
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP
from arkanlor.dagrm.list12bit import read_12bitlist, write_12bitlist
from arkanlor.dagrm.extended import DatagramIf, DatagramPacket

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

class UnicodeTalkRequestSpeechMulList(SubPackets):
    """
        datagram manipulation to read and write the 12 bit lists for speech.mul
        references.
        
        if no other packet than UnicodeTalkRequest needs this, it may be wise
        to include a CSTRING / UCSTRING message handling into it.
    """
    __slots__ = ['items', 'type' ] # contains the node name it saves or restores speechmuldata from.
    def __init__(self, items, ttype):
        self.items = items
        self.type = ttype

    def packet_read(self, values, data, instance=None):
        # we read the 12 bit list into key self.items, if type & 0xc0
        value_type = values.get(self.type, 0)
        if value_type & 0xc0:
            values[self.items], data = read_12bitlist(data)
        return values, data

    def packet_write(self, values, data, instance=None):
        # we write items into the data stream, if it has length
        # note that packet type has already been written.
        # we do not append the list if type is not in order.
        items = values.get(self.items, [])
        value_type = values.get(self.type, 0)
        if value_type & 0xc0:
            data = write_12bitlist(items, data)
        return values, data

class UnicodeTalkRequest(Packet):
    # note this packet can be highly complex,
    # the condition is ttype & 0xc0 -> message gets a 12 bit list prepended.
    # first 12 bits: length of 12 bit list
    # then length * 12 bits -> keywords
    # (and +4 if number is even, to fill up the bytes)
    p_id = 0xad
    p_type = P_CLIENT
    _datagram = [('ttype', BYTE, None, 0x0),
                 ('color', USHORT),
                 ('font', USHORT),
                 ('lang', FIXSTRING, 3), # 4 bytes.
                 (0, BYTE), # terminator
                 UnicodeTalkRequestSpeechMulList('speech_list', 'ttype'),
                 # note: message becomes cstring if speechmul present?
                 # further investigation needed.
                 DatagramIf('ttype', lambda x: x & 0x0c,
                            when_true=DatagramPacket(('message', CSTRING)),
                            else_do=DatagramPacket(('message', UCSTRING)),
                            )
                 ]

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

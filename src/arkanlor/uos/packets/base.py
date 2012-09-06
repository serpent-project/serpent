# -*- coding: utf-8 -*-

"""
    Ultima Online Packets
    especially for server use, however all packets should be designed to be in/out.
    @see gemuo for a client side only implementation.
    @see packet_io
"""
from arkanlor.dagrm import BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets
from arkanlor.uos.packet import UOPacket as Packet
from arkanlor.uos.const import LoginDeniedReason
P_CLIENT, P_SERVER, P_BOTH, P_EXP = 0, 1, 2, 3

#### Universal Packets
class Dummy(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x32 # ascii code for 2. useful for netcat.
    p_type = P_BOTH
    _datagram = [ ('byte', BYTE,), ]

class NoEncryption(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xFF
    p_type = P_BOTH
    _datagram = [ (0, BYTE),
                  (1, BYTE),
                  (2, BYTE)]

    def __unicode__(self):
        return u"Caught Encryption Packet in mid stream?"



class PingMessage(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x73
    p_type = P_BOTH
    _datagram = [ ('sequence', BYTE), ]

    def __unicode__(self):
        return u'Ping Sequence %i' % (self.values.get('sequence'),)


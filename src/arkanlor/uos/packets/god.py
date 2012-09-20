# -*- coding: utf-8 -*-
"""
    Packets designed for the God client.

    For God so loved the world, that he gave his only begotten Son, that 
    whosoever believeth in him should not perish, but have everlasting life.

    John 3:16
"""
from arkanlor.dagrm import BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets
from arkanlor.uos.packet import UOPacket as Packet
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP
from arkanlor.dagrm.extended import DatagramCountLoop
from arkanlor.dagrm.const import COUNT, SBYTE

class _Cell(Packet):
    _datagram = [('tile', USHORT),
                 ('z', SBYTE)]

class UpdateTerrain(Packet):
    """
    http://necrotoolz.sourceforge.net/kairpacketguide/packet40.htm
    
        used by the god client.
        note: the block_num is used as 2 ushorts for blockx/blocky
        in this implementation.
        the header is used to represent already synced data.
    """
    p_id = 0x40
    p_length = 0x00c9
    _datagram = [('bx', USHORT),
                 ('by', USHORT), # actually, UINT: 512 * y + x
                 DatagramCountLoop(64, 'cells', _Cell),
                 ('header', UINT)
                 ]

class _Static(Packet):
    _datagram = [('graphic', USHORT),
                 ('rx', BYTE),
                 ('ry', BYTE),
                 ('z', SBYTE),
                 ('color', USHORT),
                 ]

class UpdateStatics(Packet):
    """
    http://necrotoolz.sourceforge.net/kairpacketguide/packet3f.htm
        
        used normally by the god client.
        note: block_num is used as 2 ushorts for blockx/blocky in this
        implementation, header is used to represent already synced data.
    """
    p_id = 0x3F
    p_length = 0
    _datagram = [('bx', USHORT),
                 ('by', USHORT), # actually, UINT: 512 * y + x
                 ('count', COUNT, UINT, 'statics'),
                 ('header', UINT), # extra
                 DatagramCountLoop('count', 'statics', _Static),
                 ]

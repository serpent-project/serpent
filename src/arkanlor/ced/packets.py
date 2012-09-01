# -*- coding: utf-8 -*-

"""
    CentrED Server Packets
    
    @see uos packets.
"""
from arkanlor.uos.packet_io import Packet, packet_list, BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, SubPackets

P_CED = 0x5

# these are subpackets of packet 0x0C
class ClientConnected(Packet):
    """
        subpacket of client command packet.
        a client connected.
    """
    __slots__ = Packet.__slots__
    p_id = 0x01
    p_length = 0
    p_type = P_CED
    _datagram = [ ('username', CSTRING), ]

class ClientDisconnected(Packet):
    """
        subpacket of client command packet.
        a client disconnected.
    """
    __slots__ = Packet.__slots__
    p_id = 0x02
    p_length = 0
    p_type = P_CED
    _datagram = [ ('username', CSTRING), ]

class ClientList(Packet):
    """
        subpacket of client command packet.
        lists all clients.
    """
    __slots__ = Packet.__slots__
    p_id = 0x03
    p_length = 0
    p_type = P_CED
    _datagram = []
    # cstring list of usernames.
    # UClientHandling

class AccessChanged(Packet):
    """
        subpacket of client comamnd packet,
        notifys about access level
        and regions accessible 
    """
    __slots__ = Packet.__slots__
    p_id = 0x07
    p_length = 0
    p_type = P_CED
    _datagram = [ ('access_level', BYTE),
                 ]
    # WriteAccountRestrictions
# 

# These can also come from the client:
class UpdatePosition(Packet):
    """
        incoming: request client position
        outgoing: via clientcommand packet, set position
    """
    __slots__ = Packet.__slots__
    p_id = 0x04
    p_length = 0
    p_type = P_CED
    _datagram = [ ('x', USHORT),
                  ('y', USHORT),
                 ]

class Message(Packet):
    """
        incoming/outgoing chat message
        sent by server via clientcommand packet
    """
    __slots__ = Packet.__slots__
    p_id = 0x05
    p_length = 0
    p_type = P_CED
    _datagram = [ ('name', CSTRING),
                  ('message', CSTRING),
                 ]

class ClientCommand(Packet):
    """
        Packet with subpackets similar to General Information in uos.
        Is handled by sub packet system
    """
    __slots__ = Packet.__slots__
    p_id = 0x0c
    p_length = 0
    p_type = P_CED
    _datagram = [ SubPackets(ClientConnected,
                             ClientDisconnected,
                             ClientList,
                             AccessChanged,
                             UpdatePosition,
                             Message
                             ) ]

class Compressed(Packet):

    p_id = 0x1
    p_length = 0

class Block(Packet):

    p_id = 0x4
    p_length = 0



class DrawMap(Packet):

    p_id = 0x6
    p_length = 8

class InsertStatic(Packet):

    p_id = 0x7
    p_length = 10

class DeleteStatic(Packet):

    p_id = 0x8
    p_length = 10

class ElevateStatic(Packet):

    p_id = 0x9
    p_length = 11

class MoveStatic(Packet):

    p_id = 0xa
    p_length = 14

class HueStatic(Packet):

    p_id = 0xb
    p_length = 12



server_packets = packet_list(Message,
                             UpdatePosition,

                             Compressed,
                             Block,
                             DrawMap,
                             InsertStatic,
                             DeleteStatic,
                             ElevateStatic,
                             MoveStatic,
                             HueStatic,
                             )

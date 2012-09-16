# -*- coding: utf-8 -*-

"""
    MC Server Packets
    http://www.minecraftwiki.net/wiki/Classic_server_protocol
    http://www.wiki.vg/Protocol
    
"""
from arkanlor.dagrm import packet_list, BYTE, SHORT, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, SBYTE, SubPackets, ReadWriteDatagram, \
    WORD, CARDINAL, COUNT, FLOAT, DOUBLE, US646, INT, UCSTRING
from arkanlor.notch.packet import MCPacket as Packet, MCPacketReader
from arkanlor.dagrm.extended import DatagramCountLoop, DatagramIf, \
    DatagramPacket, DatagramSub, DatagramEndLoop
import zlib
from arkanlor.uos.packets.base import P_BOTH, P_CLIENT, P_SERVER


class DisconnectServerInfo(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xff
    p_type = P_BOTH
    p_length = None
    _datagram = [('reason', US646), # {0}§{1}§{2}
                 #('other', US646),
                 #(0, USHORT, None, 0xa7),
                 #('online', USHORT),
                 ]

class PingVersion(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xfe
    p_type = P_CLIENT
    p_length = 1
    _datagram = []

class Handshake(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x02
    p_type = P_CLIENT
    p_length = None
    _datagram = [
                 ('version', SBYTE),
                 # if version is zero
                 DatagramIf('version', lambda x: x == 0,
                            when_true=DatagramSub([('username', RAW)]),
                            else_do=DatagramSub(
                                        [('username', US646),
                                         ('host', US646),
                                         ('port', INT), ]
                                                ))
                 ]

    def __unicode__(self):
        return u'Handshake with user %s, Version %s' % (
                                                self.values.get('username', ''),
                                                hex(self.values.get('version', 0x0))
                                                        )
# encryption stuff:
# 0xfd - request server
# 0xfc - answer client and server again
# encryption should be enabled now.
# client sends payload with 0 byte (0xcd)
# kick here if needed.

class LoginRequest(Packet):
    __slots__ = Packet.__slots__
    p_type = P_SERVER # seriously?
    p_id = 0x01
    p_length = None
    _datagram = [
            ('entity_id', INT),
            ('level_type', US646, None, 'default'),
            ('game_mode', SBYTE), # 0:survival, 1:creative, 2:adventure, 0x8:hardcore flag
            ('dimension', SBYTE), # -1 nether, 0 normal, 1 end
            ('difficulty', SBYTE, None, 1), # peaceful, easy, normal, hard 0-3
            ('world_height', BYTE),
            ('max_players', BYTE, None, 8),
                 ]

# we continue with:

# chunks and entities
class ChunkData(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x33
    _datagram = [('chunk_x', INT),
                 ('chunk_z', INT),
                 ('continuous', BOOLEAN), # all sections in this vertical column?
                 ('bitmask', USHORT),
                 ('bitmask_add', USHORT),
                 ('compressed_size', INT),
                 (0, INT), # unused for 1.2.5
                 ('compressed_data', RAW)
                 ]

class Entity(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x1e
    p_length = 5
    _datagram = [('entity_id', INT)]

# spawn position
class SpawnPosition(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x06
    p_length = 13
    _datagram = [('x', INT),
                 ('y', INT),
                 ('z', INT)]

# inventory

# position + look packet.
# answers with position + look
class PlayerPositionLook(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x0d
    p_type = P_BOTH
    _datagram = ReadWriteDatagram(
                    [('x', DOUBLE),
                     ('y', DOUBLE),
                     ('stance', DOUBLE),
                     ('z', DOUBLE),
                     ('yaw', FLOAT), # absolute rotation x axis
                     ('pitch', FLOAT), # absolute rotation y axis
                     ('on_ground', BOOLEAN),
                     ], # from client
                    [
                     ('x', DOUBLE),
                     ('stance', DOUBLE),
                     ('y', DOUBLE),
                     ('z', DOUBLE),
                     ('yaw', FLOAT), # absolute rotation x axis
                     ('pitch', FLOAT), # absolute rotation y axis
                     ('on_ground', BOOLEAN),
                     ] # from server
                                  )

class PlayerPosition(Packet):
    """ sent by client """
    __slots__ = Packet.__slots__
    p_type = P_CLIENT
    p_id = 0x0b
    p_size = 34
    _datagram = [('x', DOUBLE),
                 ('y', DOUBLE),
                 ('stance', DOUBLE),
                 ('z', DOUBLE),
                 ('on_ground', BOOLEAN),
                 ]

class PlayerLook(Packet):
    __slots__ = Packet.__slots__
    p_type = P_CLIENT
    p_id = 0x0c
    p_size = 10
    _datagram = [('yaw', FLOAT),
                 ('pitch', FLOAT),
                 ('on_ground', BOOLEAN)]

class Message(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x03
    p_length = None
    p_type = P_BOTH
    _datagram = [('message', US646)]


server_parsers = packet_list(
                    PingVersion,
                    Handshake,
                    PlayerLook,
                    PlayerPosition,
                    PlayerPositionLook,
                    Message,
                             )

packet_reader = MCPacketReader(server_parsers)

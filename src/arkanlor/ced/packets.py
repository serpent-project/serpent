# -*- coding: utf-8 -*-

"""
    CentrED Server Packets
    
    @see uos packets.
"""
from arkanlor.dagrm import packet_list, BYTE, SHORT, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, SBYTE, SubPackets, ReadWriteDatagram, \
    WORD, CARDINAL
from arkanlor.ced.packet import CEDPacket as Packet, CEDPacketReader
from arkanlor.ced.const import PROTOCOL_VERSION, LoginStates, ServerStates, \
    AccessLevel, ModifyRegionStatus, DeleteRegionStatus, DeleteUserStatus, \
    ModifyUserStatus
from arkanlor.dagrm.extended import DatagramCountLoop, DatagramIf, \
    DatagramPacket, DatagramSub, DatagramEndLoop
import zlib
from arkanlor.dagrm.const import COUNT

P_CED = 0x5

##############################################################################
# Client Command Subpacket System
def AsCC(packet_type, values):
    values['subcmd'] = packet_type.p_id
    return ClientCommand(values)

class CCSubPacket(Packet):
    __slots__ = Packet.__slots__
    p_type = 0x0c

    def serialize(self):
        cc = AsCC(self, self.values)
        return cc.serialize()

    def read_data(self, length):
        if len(self._data) < length:
            return '\0' * length
        x, self._data = self._data[:length], self._data[length:]
        return x

# these are subpackets of packet 0x0C
class ClientConnected(CCSubPacket):
    """
        subpacket of client command packet.
        a client connected.
    """
    __slots__ = Packet.__slots__
    p_id = 0x01
    p_length = 0
    p_type = P_CED
    _datagram = [ ('username', CSTRING), ]

class ClientDisconnected(CCSubPacket):
    """
        subpacket of client command packet.
        a client disconnected.
    """
    __slots__ = Packet.__slots__
    p_id = 0x02
    p_length = 0
    p_type = P_CED
    _datagram = [ ('username', CSTRING), ]

class ClientList(CCSubPacket):
    """
        subpacket of client command packet.
        lists all (connected) clients.
    """
    __slots__ = Packet.__slots__
    p_id = 0x03
    p_length = 0
    p_type = P_CED
    _datagram = []
    # cstring list of usernames.
    # UClientHandling



# These can also come from the client:
class UpdatePosition(CCSubPacket):
    """
        incoming: request client position
        outgoing: via clientcommand packet, set position
    """
    __slots__ = Packet.__slots__
    p_id = 0x04
    p_length = 0
    p_type = P_CED
    _datagram = [ ('x', WORD),
                  ('y', WORD),
                 ]

class Message(CCSubPacket):
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

class GotoClient(CCSubPacket):
    """
        Client Command packet.
    """
    __slots__ = Packet.__slots__
    p_id = 0x06
    p_length = 0
    p_type = P_CED
    _datagram = [ ('name', CSTRING), ]

class AccessChanged(CCSubPacket):
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

subpackets_clientcommand = SubPackets('subcmd',
                             ClientConnected,
                             ClientDisconnected,
                             ClientList,
                             AccessChanged,
                             UpdatePosition,
                             Message,
                             GotoClient,
                             )

class ClientCommand(Packet):
    """
        Packet with subpackets similar to General Information in uos.
        Is handled by sub packet system
    """
    __slots__ = Packet.__slots__
    p_id = 0x0c
    p_length = 0
    p_type = P_CED
    _datagram = [ ('subcmd', BYTE),
                  subpackets_clientcommand]

    def _unpack(self):
        # detect our type
        p_id = self.values.get('subcmd', None)
        if not p_id:
            return self
        p = subpackets_clientcommand.packets.get(p_id, None)
        if not p:
            return self
        p = p(self.values)
        p._data = self._data
        return p
##############################################################################
# 0x1 : compressed packets.

class Compressed(Packet):
    __slots__ = Packet.__slots__ + ['subp']
    p_id = 0x1
    p_length = 0
    _datagram = []

    def __init__(self, packet):
        self.subp = None
        super(Compressed, self).__init__(packet)

    def set_initial_arg(self, arg):
        # we presume, the subpacket is the value
        if isinstance(arg, Packet):
            self.subp = arg

    def _serialize(self):
        # we serialize our subpacket and zlib it.
        pdata = self.subp.serialize()
        self.w_uint(len(pdata))
        self._data += zlib.compress(pdata, 9)

    def _unpack(self):
        size = self.r_uint()
        pdata = zlib.decompress(self._data[:size])
        data = packet_reader.read_from_buffer(pdata)
        if data is not None:
            return packet_reader.init_packet(data[1], data[2])
        return self



##############################################################################
# Login Command Subpackets.
def AsLC(packet_type, values):
    values['subcmd'] = packet_type.p_id
    return LoginCommand(values)

class LCSubPacket(Packet):
    __slots__ = Packet.__slots__
    p_type = 0x02

    def serialize(self):
        lc = AsLC(self, self.values)
        return lc.serialize()

    def read_data(self, length):
        if len(self._data) < length:
            return '\0' * length
        x, self._data = self._data[:length], self._data[length:]
        return x


class ProtocolVersion(LCSubPacket):
    p_id = 0x1
    _datagram = [('version', CARDINAL, None, PROTOCOL_VERSION)]

class LoginRequest(LCSubPacket): # only sent by client
    p_id = 0x3
    _datagram = [('username', CSTRING),
                 ('password', CSTRING)]

class ServerState(LCSubPacket):
    p_id = 0x4
    _datagram = [('state', BYTE, None, ServerStates.Running),
                 ]
    # if ServerStates.Other: ('message', CSTRING)

class Quit(LCSubPacket):
    p_id = 0x5
    _datagram = []

subpackets_login = SubPackets('subcmd',
                              ProtocolVersion,
                              LoginRequest,
                              ServerState,
                              Quit,
                              )

class LoginCommand(Packet):
    """
        Packet with subpackets.
        handles server side (loginresponse is below)
    """
    __slots__ = Packet.__slots__
    p_id = 0x2
    p_length = 0
    _datagram = [('subcmd', BYTE),
                 subpackets_login]

    def _unpack(self):
        # detect our type
        p_id = self.values.get('subcmd', None)
        if not p_id:
            return self
        p = subpackets_login.packets.get(p_id, None)
        if not p:
            return self
        p = p(self.values)
        p._data = self._data
        return p

class LoginResponse(Packet):
    # only sent by server
    # this is subpacket 0x3 (LoginRequest) on client side.
    # 
    __slots__ = Packet.__slots__
    p_id = 0x2
    p_length = 0
    _datagram = [('subcmd', BYTE, None, 0x3),
                 ('state', BYTE),
                 # only if lsOk - subpackets?
                 ('access_level', BYTE, None, AccessLevel.View),
                 ('map_width', WORD),
                 ('map_height', WORD),
                 # account restrictions.
                 ]

def AsAC(packet_type, values):
    values['subcmd'] = packet_type.p_id
    return AdminCommand(values)

class ACSubPacket(Packet):
    __slots__ = Packet.__slots__
    p_type = 0x03

    def serialize(self):
        ac = AsAC(self, self.values)
        return ac.serialize()

    def read_data(self, length):
        if len(self._data) < length:
            return '\0' * length
        x, self._data = self._data[:length], self._data[length:]
        return x

class FlushServer(ACSubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x1
    p_length = 0
    _datagram = []

class QuitServer(ACSubPacket):
    __slots__ = Packet.__slots__
    p_id = 0x2
    p_length = 0
    _datagram = [('message', CSTRING), ]

    def __unicode__(self):
        return u'Quitting (reason: %s)' % self.values.get('message', None)

# Region related packet.
# Helper classes:
class _Area(Packet):
    _datagram = [('x1', WORD),
                 ('y1', WORD),
                 ('x2', WORD),
                 ('y2', WORD)]

class _Region(Packet):
    _datagram = [('name', CSTRING),
                 ('count', COUNT, BYTE, 'areas'),
                 DatagramCountLoop('count', 'areas', _Area)]

class ModifyRegion(ACSubPacket):
    p_id = 0x8
    _datagram = ReadWriteDatagram(
                # read (aka from client)
                    [('name', CSTRING),
                     ('count', COUNT, BYTE, 'areas'),
                     DatagramCountLoop('count', 'areas', _Area),
                     ],
                # write (aka to client)
                    [('status', BYTE),
                     ('name', CSTRING),
                     DatagramIf('status',
                                lambda x: x in [ModifyRegionStatus.Added,
                                                ModifyRegionStatus.Modified],
                                when_true=DatagramSub([
                                 ('count', COUNT, BYTE, 'areas'),
                                 DatagramCountLoop('count', 'areas', _Area),
                                ]),
                                ),
                     ])

class DeleteRegion(ACSubPacket):
    p_id = 0x9
    _datagram = ReadWriteDatagram(
                # read (aka from client)
                    [('name', CSTRING), ],
                # write (aka to client)
                    [('status', BYTE, None, DeleteRegionStatus.NotFound),
                     ('name', CSTRING)],
                )
class RegionList(ACSubPacket):
    p_id = 0xa
    _datagram = ReadWriteDatagram(
                # read (aka from client)
                    [],
                # write (aka to client)
                    [
                     ('count', COUNT, BYTE, 'regions'),
                     DatagramCountLoop('count', 'regions', _Region),
                     ],
                )
#####
# User Management.

class _RegionName(Packet):
    _datagram = [('name', CSTRING), ]

class _User(Packet):
    _datagram = [('name', CSTRING),
                 ('access_level', BYTE, None, AccessLevel.NoAccess),
                 ('count', COUNT, BYTE, 'regions'),
                 DatagramCountLoop('count', 'regions', _RegionName)
                 ]

class ModifyUser(ACSubPacket):
    # highly doubtful, that i am going to use this for more than setting your
    # own password or modifying regions until ced account settings are separated.
    __slots__ = Packet.__slots__
    p_id = 0x5
    _datagram = ReadWriteDatagram(
                [('username', CSTRING),
                 ('password', CSTRING),
                 ('access_level', BYTE),
                 ('count', COUNT, BYTE, 'regions'),
                 DatagramCountLoop('count', 'regions', _RegionName)
                 ],
                [('status', BYTE),
                 ('name', CSTRING),
                 DatagramIf('status',
                                lambda x: x in [ModifyUserStatus.Added,
                                                ModifyUserStatus.Modified],
                                when_true=DatagramSub([
                                  ('access_level', BYTE),
                                  ('count', COUNT, BYTE, 'regions'),
                                  DatagramCountLoop('count', 'regions', _RegionName),
                                ]),
                                ),
                 ]
                )

class DeleteUser(ACSubPacket):
    p_id = 0x6
    _datagram = ReadWriteDatagram(
                [('name', CSTRING)],
                [('status', BYTE, None, DeleteUserStatus.NotFound),
                 ('name', CSTRING)])

class UserList(ACSubPacket):
    p_id = 0x7
    _datagram = ReadWriteDatagram(
                [],
                [('count', COUNT, WORD, 'users'), #of accounts.
                 DatagramCountLoop('count', 'users', _User)
                 ])



subpackets_admin = SubPackets('subcmd',
                              FlushServer,
                              QuitServer,
                              ModifyUser,
                              DeleteUser,
                              UserList,
                              ModifyRegion,
                              DeleteRegion,
                              RegionList,
                              )


class AdminCommand(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x3
    p_length = 0
    _datagram = [('subcmd', BYTE),
                 subpackets_admin]
    def _unpack(self):
        # detect our type
        p_id = self.values.get('subcmd', None)
        if not p_id:
            return self
        p = subpackets_admin.packets.get(p_id, None)
        if not p:
            return self
        p = p(self.values)
        p._data = self._data
        return p

##############################################################################
# from 0x4: standard packets.

class _Static(Packet):
    _datagram = [('graphic', WORD),
                 ('rx', BYTE),
                 ('ry', BYTE),
                 ('z', SBYTE),
                 ('color', SHORT),
                 ]

class _MapCell(Packet):
    _datagram = [('graphic', WORD),
                 ('z', SBYTE)]

class _MapBlock(Packet):
    _datagram = [('bx', WORD),
                 ('by', WORD),
                 ('header', UINT),
                 DatagramCountLoop(64, 'cells', _MapCell),
                 ('count', COUNT, WORD, 'statics'), # no of statics.
                 DatagramCountLoop('count', 'statics', _Static)
                ]

class _Coords(Packet):
    _datagram = [('bx', WORD),
                 ('by', WORD)]

class Block(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x4
    p_length = 0
    _datagram = ReadWriteDatagram(
                    [DatagramEndLoop('coords', _Coords)],
                    [DatagramEndLoop('blocks', _MapBlock)])

class FreeBlock(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x5
    p_length = 5
    _datagram = [('x', WORD),
                 ('y', WORD), ]

class DrawMap(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x6
    p_length = 8
    _datagram = [('x', WORD),
                 ('y', WORD),
                 ('z', SBYTE),
                 ('graphic', WORD)]

class InsertStatic(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x7
    p_length = 10
    _datagram = [('x', WORD),
                 ('y', WORD),
                 ('z', SBYTE),
                 ('graphic', WORD),
                 ('color', WORD),
                 ]

class DeleteStatic(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x8
    p_length = 10
    _datagram = [('x', WORD),
                 ('y', WORD),
                 ('z', SBYTE),
                 ('graphic', WORD),
                 ('color', WORD)]

class ElevateStatic(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x9
    p_length = 11
    _datagram = [('x', WORD),
                 ('y', WORD),
                 ('z', SBYTE),
                 ('graphic', WORD),
                 ('color', WORD),
                 ('znew', SBYTE)]

class MoveStatic(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xa
    p_length = 14
    _datagram = [('x', WORD),
                 ('y', WORD),
                 ('z', SBYTE),
                 ('graphic', WORD),
                 ('color', WORD),
                 ('xnew', WORD),
                 ('ynew', WORD), ]

class HueStatic(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xb
    p_length = 12
    _datagram = [('x', WORD),
                 ('y', WORD),
                 ('z', SBYTE),
                 ('graphic', WORD),
                 ('color', WORD),
                 ('hue', WORD), # or name it colornew? 
                 ]

##############################################################################
class RequestRadar(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x0d
    p_length = 2
    _datagram = [('type', BYTE)] # 0x1: checksum, 0x2: radar mappacket.


##############################################################################
class NoOp(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xff
    p_length = 1
    _datagram = []



server_parsers = packet_list(
                             Compressed,
                             LoginCommand,
                             AdminCommand,
                             Block,
                             FreeBlock,
                             DrawMap,
                             InsertStatic,
                             DeleteStatic,
                             ElevateStatic,
                             MoveStatic,
                             HueStatic,

                             ClientCommand,

                             RequestRadar,
                             NoOp,
                             )

packet_reader = CEDPacketReader(server_parsers)

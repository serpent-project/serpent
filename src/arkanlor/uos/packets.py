# -*- coding: utf-8 -*-

"""
"""
import packet_io as pio
import data
P_CLIENT, P_SERVER, P_BOTH, P_EXP = 0, 1, 2, 3

packet_lengths = [
    0x0068, 0x0005, 0x0007, 0x0000, 0x0002, 0x0005, 0x0005, 0x0007, # 0x00
    0x000e, 0x0005, 0x0007, 0x0007, 0x0000, 0x0003, 0x0000, 0x003d, # 0x08
    0x00d7, 0x0000, 0x0000, 0x000a, 0x0006, 0x0009, 0x0001, 0x0000, # 0x10
    0x0000, 0x0000, 0x0000, 0x0025, 0x0000, 0x0005, 0x0004, 0x0008, # 0x18
    0x0013, 0x0008, 0x0003, 0x001a, 0x0007, 0x0014, 0x0005, 0x0002, # 0x20
    0x0005, 0x0001, 0x0005, 0x0002, 0x0002, 0x0011, 0x000f, 0x000a, # 0x28
    0x0005, 0x0001, 0x0002, 0x0002, 0x000a, 0x028d, 0x0000, 0x0008, # 0x30
    0x0007, 0x0009, 0x0000, 0x0000, 0x0000, 0x0002, 0x0025, 0x0000, # 0x38
    0x00c9, 0x0000, 0x0000, 0x0229, 0x02c9, 0x0005, 0x0000, 0x000b, # 0x40
    0x0049, 0x005d, 0x0005, 0x0009, 0x0000, 0x0000, 0x0006, 0x0002, # 0x48
    0x0000, 0x0000, 0x0000, 0x0002, 0x000c, 0x0001, 0x000b, 0x006e, # 0x50
    0x006a, 0x0000, 0x0000, 0x0004, 0x0002, 0x0049, 0x0000, 0x0031, # 0x58
    0x0005, 0x0009, 0x000f, 0x000d, 0x0001, 0x0004, 0x0000, 0x0015, # 0x60
    0x0000, 0x0000, 0x0003, 0x0009, 0x0013, 0x0003, 0x000e, 0x0000, # 0x68
    0x001c, 0x0000, 0x0005, 0x0002, 0x0000, 0x0023, 0x0010, 0x0011, # 0x70
    0x0000, 0x0009, 0x0000, 0x0002, 0x0000, 0x000d, 0x0002, 0x0000, # 0x78
    0x003e, 0x0000, 0x0002, 0x0027, 0x0045, 0x0002, 0x0000, 0x0000, # 0x80
    0x0042, 0x0000, 0x0000, 0x0000, 0x000b, 0x0000, 0x0000, 0x0000, # 0x88
    0x0013, 0x0041, 0x0000, 0x0063, 0x0000, 0x0009, 0x0000, 0x0002, # 0x90
    0x0000, 0x001a, 0x0000, 0x0102, 0x0135, 0x0033, 0x0000, 0x0000, # 0x98
    0x0003, 0x0009, 0x0009, 0x0009, 0x0095, 0x0000, 0x0000, 0x0004, # 0xA0
    0x0000, 0x0000, 0x0005, 0x0000, 0x0000, 0x0000, 0x0000, 0x000d, # 0xA8
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0040, 0x0009, 0x0000, # 0xB0
    0x0000, 0x0003, 0x0006, 0x0009, 0x0003, 0x0000, 0x0000, 0x0000, # 0xB8
    0x0024, 0x0000, 0x0000, 0x0000, 0x0006, 0x00cb, 0x0001, 0x0031, # 0xC0
    0x0002, 0x0006, 0x0006, 0x0007, 0x0000, 0x0001, 0x0000, 0x004e, # 0xC8
    0x0000, 0x0002, 0x0019, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, # 0xD0
    0x0000, 0x010C, 0xFFFF, 0xFFFF, 0x0009, 0x0000, 0xFFFF, 0xFFFF, # 0xD8
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xE0
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xE8
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, # 0xF0
    0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0x0003, # 0xF8
]

class Packet(object):
    # see euclid.py for further optimizations.
    __slots__ = [ 'p_id', 'p_type', 'p_length', '_datagram', '_data', 'values' ]
    p_id = None
    p_type = None
    p_length = None
    _data = None
    _datagram = []
    values = None

    def __init__(self, packet_or_values=None):
        if isinstance(packet_or_values, basestring):
            self._data = packet_or_values
            self.values = {}
        elif isinstance(packet_or_values, dict):
            self.values = packet_or_values
            self._data = ''
        if self.p_id and self.p_length == None:
            self.p_length = packet_lengths[self.p_id]


    def __getattr__(self, key):
        if self.values and key not in self.__slots__ and key in self.values.keys():
            return self.values[key]
        return super(Packet, self).__getattr__(key)

    def __setattr__(self, key, value):
        if self.values and key not in self.__slots__ and key in self.values.keys():
            self.values[key] = value
            return
        return super(Packet, self).__setattr__(key, value)

    def read_data(self, length):
        if len(self._data) < length:
            raise Exception("Packet is too short")
        x, self._data = self._data[:length], self._data[length:]
        return x

    def unpack(self):
        if self._datagram:
            for item in self._datagram:
                l, t, key, item = None, item[0], item[1], item[2:]
                if item: # optional argument length
                    l = item[0]
                data = None
                if not t:
                    self.values[key] = pio.r_boolean(self.read_data)
                elif t == pio.BYTE:
                    self.values[key] = pio.r_byte(self.read_data)
                elif t == pio.USHORT:
                    self.values[key] = pio.r_ushort(self.read_data)
                elif t == pio.UINT:
                    self.values[key] = pio.r_uint(self.read_data)
                elif t == pio.FIXSTRING:
                    self.values[key] = pio.r_fixstring(self.read_data, l)
                elif t == pio.CSTRING:
                    self.values[key] = pio.r_cstring(self.read_data, self._data)
                elif t == pio.PSTRING:
                    self.values[key] = pio.r_pstring(self.read_data)
                elif t == pio.IPV4:
                    self.values[key] = pio.r_ipv4(self.read_data)
                else:
                    if l:
                        self.values[key] = self.read_data(l)
                    else:
                        raise Exception('Unknown Packet in Datagram')
        return self

    def serialize(self):
        if self._datagram:
            for item in self._datagram:
                l, t, key, item = None, item[0], item[1], item[2:]


#### Universal Packets
class Dummy:
    p_id = 0x32 # ascii code for 2. useful for netcat.
    p_type = P_BOTH
    def __init__(self, packet):
        self.byte = packet.byte()

    @classmethod
    def PacketWriter(cls, b):
        p = PacketWriter(cls.p_id)
        p.byte(b)
        return p.finish()

class NoEncryption:
    p_id = 0xFF
    p_type = P_BOTH

    def __init__(self, packet):
        packet.byte()
        packet.byte()
        packet.byte()

    @classmethod
    def PacketWriter(cls):
        p = PacketWriter(0xff)
        p.byte(0xff)
        p.byte(0xff)
        p.byte(0xff)
        return p.finish()

    def __unicode__(self):
        return u"Caught NoEncryption Packet in mid stream?"

class LoginComplete:
    """
    """
    p_id = 0x55 # the packet id is the first byte in the packet. important for writing packets.
    p_type = P_BOTH # who sends this packets?
    def __init__(self, packet):
        pass

    @classmethod
    def PacketWriter(cls):
        p = PacketWriter(cls.p_id)
        # write packet data here if needed.
        return p.finish()

    def __unicode__(self):
        return ""

#### Client Sent Packets
# these packets need packet parsing classes for the server.

class AccountLogin:
    p_id = 0x80
    p_type = P_CLIENT
    def __init__(self, packet):
        self.username = packet.fixstring(30)
        self.password = packet.fixstring(30)
        self.next_login_key = packet.byte()

    @classmethod
    def PacketWriter(cls, username, password):
        p = PacketWriter(cls.p_id)
        p.fixstring(username, 30)
        p.fixstring(password, 30)
        p.byte(0) #NextLoginKey value from uo.cfg on client machine.
        return p.finish()

    def __unicode__(self):
        return u"Account %s tries to login (next key: %s)" % (self.username, hex(self.next_login_key))

class GameLogin:
    p_id = 0x91
    p_type = P_CLIENT
    def __init__(self, packet):
        self.auth_id = packet.uint()
        self.username = packet.fixstring(30)
        self.password = packet.fixstring(30)

    @classmethod
    def PacketWriter(cls, username, password, auth_id):
        p = PacketWriter(cls.p_id)
        p.uint(auth_id)
        p.fixstring(username, 30)
        p.fixstring(password, 30)
        return p.finish()

    def __unicode__(self):
        return u"Username %s at game login" % (self.username,)


class SelectServer:
    p_id = 0xa0
    p_type = P_CLIENT

    def __init__(self, packet):
        self.selected = packet.byte()

    @classmethod
    def PacketWriter(cls, selected):
        p = PacketWriter(cls.p_id)
        p.byte(selected)
        return p.finish()

    def __unicode__(self):
        return u"Server selected: %s" % (self.selected,)

class LoginCharacter:
    p_id = 0x5d
    p_size = 73
    p_type = P_CLIENT

    def __init__(self, packet):
        pattern1 = packet.uint()
        self.charname = packet.fixstring(30)
        packet.ushort() # unknown0
        self.client_flag = packet.uint()
        packet.uint() # unknown1
        self.login_count = packet.uint()
        packet.fixstring(16) # unknown
        self.slot = packet.uint()
        self.client_ip = packet.uint()

    def __unicode__(self):
        return u"Character %s logging in from %s (%s)" % (self.charname, self.client_ip, self.client_flag)

class GetPlayerStatus:
    p_id = 0x34
    p_type = P_CLIENT

    def __init__(self, packet):
        packet.uint() # unknown
        self.type = packet.byte()
        self.serial = packet.uint()


#### Server Sent Packets
# these packets need to get packetwriters for the server.

class LoginConfirm:
    """
        http://docs.polserver.com/packets/index.php?Packet=0x1B
    """
    p_id = 0x1b
    p_type = P_SERVER

    def __init__(self, packet):
        self.serial = packet.uint()
        packet.uint()
        self.body = packet.ushort()
        self.x, self.y, self.z = packet.ushort(), packet.ushort(), packet.ushort()
        self.direction = packet.byte()
        packet.byte()
        packet.uint()
        packet.ushort()
        packet.ushort()
        self.map_width, self.map_height = packet.ushort(), packet.ushort()

    @classmethod
    def PacketWriter(cls, serial, body, x, y, z, direction, map_width, map_height):
        p = PacketWriter(cls.p_id)
        p.uint(serial)
        p.uint(0) # always 0
        p.ushort(body) # body type
        p.ushort(x)
        p.ushort(y)
        p.ushort(z)
        p.byte(direction) # also known as facing
        # unknowns:
        p.uint(0)
        p.uint(0)
        p.byte(0)

        p.ushort(map_width) # minus 8 !
        p.ushort(map_height)

        # additional unknowns
        p.ushort(0)
        p.uint(0)
        return p.finish()

class AServer: # PacketPart
    def __init__(self, packet):
        self.index = packet.ushort()
        self.name = packet.fixstring(32)
        packet.byte()
        packet.byte()
        packet.uint()

    @classmethod
    def Append(cls, p, index, name, full=0, timezone=0, server_ip=0):
        p.ushort(index)
        p.fixstring(name, 32)
        p.byte(full)
        p.byte(timezone)
        p.uint(server_ip) # backwards. only for ping.

class ServerList:
    p_id = 0xa8
    p_type = P_SERVER
    def __init__(self, packet):
        packet.byte()
        count = packet.ushort()
        self.servers = map(lambda x: AServer(packet), range(count))

    @classmethod
    def PacketWriter(cls, servers):
        """
            servers = [ data.Server, ... ]
        """
        p = PacketWriter(cls.p_id)
        p.byte(0x5D) # for arkanlor, use 0xAA ?
        p.ushort(len(servers))
        for server in servers:
            AServer.Append(p, server.index, server.name)
        return p.finish()

class ACharacter: # PartPacket
    def __init__(self, slot, packet):
        self.slot = slot
        self.name = packet.fixstring(30)
        packet.fixstring(30)

    @classmethod
    def Append(cls, p, name):
        p.fixstring(name, 30)
        p.fixstring('', 30)

class CharacterList:
    p_id = 0xa9
    p_type = P_SERVER

    def __init__(self, packet):
        count = packet.byte()
        self.characters = map(lambda x: ACharacter(x, packet), range(count))
        # incomplete, see writer.

    def find(self, name):
        for character in self.characters:
            if character.name == name:
                return character
        return None

    @classmethod
    def PacketWriter(cls, characters):
        """
            characters = [ data.Character, ... ]
        """
        p = PacketWriter(cls.p_id)
        p.byte(len(characters))
        for character in characters:
            # @todo: slot ordering.
            ACharacter.Append(p, character.name)
        if len(characters) < 5:
            for i in range(len(characters), 5):
                ACharacter.Append(p, '')
        p.byte(1) # write one city.

        p.byte(0) # index
        p.fixstring('Start', 30)
        p.byte(0) # terminator
        p.fixstring('Startarea', 30)
        p.byte(0) # terminator

        # flags
        p.uint(0)
        return p.finish()

class StatusBarInfo:
    p_id =
    p_type = P_SERVER

    @classmethod
    def PacketWriter(cls, characters):
        p = PacketWriter(cls.p_id)
        return p.finish()



server_parsers = {
    NoEncryption.p_id: NoEncryption,
    Dummy.p_id: Dummy,
    AccountLogin.p_id: AccountLogin,
    GameLogin.p_id: GameLogin,
    SelectServer.p_id: SelectServer,
    LoginComplete.p_id: LoginComplete,
    LoginCharacter.p_id: LoginCharacter,
    }

client_parsers = {
    }

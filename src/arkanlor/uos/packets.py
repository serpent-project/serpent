# -*- coding: utf-8 -*-

"""
    Ultima Online Packets
    especially for server use, however all packets should be designed to be in/out.
    @see gemuo for a client side only implementation.
    @see packet_io
"""
from arkanlor.uos.packet_io import *
P_CLIENT, P_SERVER, P_BOTH, P_EXP = 0, 1, 2, 3


#### Universal Packets
class Dummy(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x32 # ascii code for 2. useful for netcat.
    p_type = P_BOTH
    _datagram = [ (BYTE, 'byte'), ]

class NoEncryption(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xFF
    p_type = P_BOTH
    _datagram = [ (0, BYTE),
                  (1, BYTE),
                  (2, BYTE)]

    def __unicode__(self):
        return u"Caught Encryption Packet in mid stream?"

class LoginComplete(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x55 # the packet id is the first byte in the packet. important for writing packets.
    p_type = P_BOTH # who sends this packets?
    _datagram = []

    def __unicode__(self):
        return "Login Complete"

class PingMessage(Packet):
    p_id = 0x73
    p_type = P_BOTH
    _datagram = [ ('sequence', BYTE), ]

#### Client Sent Packets
# these packets need packet parsing classes for the server.

class AccountLogin(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x80
    p_type = P_CLIENT
    _datagram = [
                 ('username', FIXSTRING, 30),
                 ('password', FIXSTRING, 30),
                 ('next_login_key', BYTE),
                 ]

    def __unicode__(self):
        return u"Account %s tries to login (next key: %s)" % (self.values['username'], hex(self.values['next_login_key']))

class GameLogin(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x91
    p_type = P_CLIENT
    _datagram = [
                 ('auth_id', UINT),
                 ('username', FIXSTRING, 30),
                 ('password', FIXSTRING, 30),
                 ]

    def __unicode__(self):
        return u"Username %s at game login" % (self.values['username'],)


class SelectServer(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xa0
    p_type = P_CLIENT
    _datagram = [('selected', BYTE), ]

    def __unicode__(self):
        return u"Server selected: %s" % (self.values['selected'],)

class LoginCharacter(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x5d
    #p_length = 73
    p_type = P_CLIENT
    _datagram = [ ('pattern1', UINT),
                  ('charname', FIXSTRING, 30),
                  (0, USHORT),
                  ('client_flag', UINT),
                  (1, UINT),
                  ('login_count', UINT),
                  (2, FIXSTRING, 16),
                  ('slot', UINT),
                  ('client_ip', IPV4) ]

    def __unicode__(self):
        return u"Character Login"
        #return u"Character %s logging in from %s (%s)" % (self.charname, self.client_ip, self.client_flag)

class GetPlayerStatus(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x34
    p_type = P_CLIENT
    _datagram = [(0, UINT),
                 ('type', BYTE),
                 ('serial', UINT)]

class ClientVersion(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xbd
    p_type = P_BOTH # note server and client differs.
    _datagram = [ ('version', CSTRING) ]

    def __unicode__(self):
        return u'Client Version %s' % (self.values.get('version', None))

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

#### Server Sent Packets
# these packets need to get packetwriters for the server.

class LoginConfirm(Packet):
    """
        http://docs.polserver.com/packets/index.php?Packet=0x1B
    """
    __slots__ = Packet.__slots__
    p_id = 0x1b
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            (0, UINT),
            ('body', USHORT),
            ('x', USHORT), ('y', USHORT), ('z', USHORT),
            ('direction', BYTE),
            (1, UINT),
            (2, UINT),
            (3, BYTE),
            ('map_width', USHORT),
            ('map_height', USHORT),
            (4, USHORT),
            (5, UINT)
            ]

class ServerList(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xa8
    p_type = P_SERVER
    _datagram = None # dynamic datagram.

    def unpack(self):
        self.values['flag'] = self.r_byte()
        count = self.r_ushort()
        servers = []
        for i in xrange(count):
            servers += [ {
                 'index': self.r_ushort(),
                 'name': self.r_fixstring(32),
                 'full': self.r_byte(),
                 'timezone': self.r_byte(),
                 'ip': self.r_ipv4()
                 }]
        self.values['count'] = count
        self.values['servers'] = servers
        return self

    def serialize(self):
        self.begin()
        v = self.values
        self.w_byte(v.get('flag', 0x00))
        self.w_ushort(len(v.get('servers', [])))
        i = 0
        for server in v.get('servers', []):
            self.w_ushort(i)
            self.w_fixstring(server.get('name', 'Arkanlor %s' % i), 32)
            self.w_byte(server.get('full', 1))
            self.w_byte(server.get('timezone', 1))
            self.w_ipv4(server.get('ip', [0, 0, 0, 0]))
            i += 1
        return self.finish(self._data)

class CharacterList(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xa9
    p_type = P_SERVER
    _datagram = None # dynamic datagram.

    def unpack(self):
        count = self.r_byte()
        characters = []
        for i in xrange(count):
            characters += [ {
                 'slot': self.r_ushort(),
                 'name': self.r_fixstring(30),
                 'password': self.r_fixstring(30),
                 }]
        self.values['count'] = count
        self.values['characters'] = characters
        # incomplete: cities!
        return self

    def serialize(self):
        self.begin()
        characters = self.values.get('characters', [])
        self.w_byte(max(len(characters), 5))
        i = 0
        for char in characters:
            self.w_fixstring(char.get('name', ''), 30)
            self.w_fixstring(char.get('password', ''), 30)
            i += 1
        while i < 5:
            self.w_fixstring('', 30)
            self.w_fixstring('', 30)
            i += 1
        # cities
        self.w_byte(1) # write one city.
        # begin cities:
        self.w_byte(0) # index
        self.w_fixstring('Start', 30)
        self.w_byte(0) # terminator
        self.w_fixstring('Startarea', 30)
        self.w_byte(0) # terminator
        # end cities.
        self.w_uint(0) # flags
        return self.finish(self._data)

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




server_parsers = {
    NoEncryption.p_id: NoEncryption,
    Dummy.p_id: Dummy,
    AccountLogin.p_id: AccountLogin,
    GameLogin.p_id: GameLogin,
    SelectServer.p_id: SelectServer,
    LoginComplete.p_id: LoginComplete,
    LoginCharacter.p_id: LoginCharacter,
    PingMessage.p_id: PingMessage,
    GetPlayerStatus.p_id: GetPlayerStatus,
    ClientVersion.p_id: ClientVersion,
    SingleClick.p_id: SingleClick,
    DoubleClick.p_id: DoubleClick,
    }

client_parsers = {
    }

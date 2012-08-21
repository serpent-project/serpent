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
    __slots__ = Packet.__slots__
    p_id = 0x73
    p_type = P_BOTH
    _datagram = [ ('sequence', BYTE), ]

    def __unicode__(self):
        return u'Ping Sequence %i' % (self.values.get('sequence'),)

class MoveAck(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x22
    p_type = P_BOTH
    _datagram = [('seq', BYTE),
                 ('notoriety', BYTE)]

class GeneralInformation(Packet):
    """    
        Very complex all-in-one-packet.
        Needs a subpacket system.
        
        called by renaissance clients:
         - 0x5
         - 0xb
         - 0xf
         
     
    """
    __slots__ = Packet.__slots__
    p_id = 0xbf
    p_type = P_BOTH
    _datagram = [ ('subcmd', USHORT) ]

    def unpack(self):
        super(GeneralInformation, self).unpack()
        subcmd = self.values.get('subcmd', None)
        print "GIP subCommand: %s" % (hex(subcmd),)
        return self

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
                 ('message', RAW)
                 ]
    # note this packet can be highly complex,
    # the condition is ttype & 0xc0 -> message gets a 12 bit list prepended.
    # first 12 bits: length of 12 bit list
    # then length * 12 bits -> keywords
    # (and +4 if number is even, to fill up the bytes)


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
    _datagram = [ ('pattern1', UINT), # 0xedededed
                  ('name', FIXSTRING, 30),
                  (0, USHORT),
                  ('client_flag', UINT),

                  # This is how Iris sees things. (The next 24 bytes)
                  # it shifts everything out of order by 1 byte.
                  (1, BYTE),
                  (2, BYTE),
                  (3, BYTE),
                  (4, UINT),
                  (5, UINT),
                  (6, UINT),
                  (7, UINT),
                  (8, UINT),
                  (9, BYTE),

                  # pol description states:
                  #(1, UINT),
                  #('login_count', UINT),
                  #(2, FIXSTRING, 16), # actually its 16 bytes

                  ('slot', UINT),
                  ('client_ip', IPV4), ]

    def __unicode__(self):
        return u"Character Login name %s, slot %s, from %s" % (self.values.get('name'),
                                                                  self.values.get('slot'),
                                                                  self.values.get('client_ip'))
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

class MoveRequest(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x02
    p_type = P_CLIENT
    _datagram = [('direction', BYTE),
                 ('seq', BYTE),
                 ('fw_prev', UINT)]


class ClientSpy(Packet):
    """ historical packet about client information """
    p_id = 0xa4
    p_type = P_CLIENT
    _datagram = [('data', FIXSTRING, 148)]

    def __unicode__(self):
        return u"I spy %s" % (self.values.get('data'),)

#### Server Sent Packets
# these packets need to get packetwriters for the server.

class Features(Packet):
    """
        http://docs.polserver.com/packets/index.php?Packet=0xb9
        Examples: 
            ML: B980FB 
            AOS-7AV: B9803B 
            AOS: B9801B 
            LBR: B90003
    """
    __slots__ = Packet.__slots__
    p_id = 0xb9
    p_type = P_SERVER
    _datagram = [('bitflag', USHORT), ]



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
            ('x', USHORT), ('y', USHORT), ('z', BYTE),
            ('z_high', BYTE),
            ('direction', BYTE),
            (1, USHORT),
            (2, UINT),
            (3, UINT),
            ('flag', BYTE),
            ('notoriety', BYTE),
            (4, UINT),
            (5, USHORT),
            (6, BYTE),
            # again iris has some own ideas here and shifts bytes
            # i guess they just filled the gaps
            #('map_width', USHORT),
            #('map_height', USHORT),
            #(4, USHORT),
            #(5, UINT)
            ]

class UpdatePlayer(Packet):
    """
        http://docs.polserver.com/packets/index.php?Packet=0x77
    """
    __slots__ = Packet.__slots__
    p_id = 0x77
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('body', USHORT),
            ('x', USHORT), ('y', USHORT), ('z', BYTE),
            ('direction', BYTE),
            ('color', USHORT),
            ('flag', BYTE),
            ('highlight', BYTE)
            ]

class Teleport(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x20
    p_type = P_SERVER
    _datagram = [
            ('serial', UINT),
            ('body', USHORT),
            (0, BYTE),
            ('color', USHORT),
            ('flag', BYTE),
            ('x', USHORT), ('y', USHORT),
            (1, USHORT),
            ('direction', BYTE),
            ('z', BYTE),
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


class GIMapChange(GeneralInformation):
    def serialize(self):
        self.begin()
        self.w_ushort(0x08)
        self.w_byte(0)
        return self.finish(self._data)

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

class Follow(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x15
    p_type = P_BOTH

    _datagram = [('target', UINT), # to follow
                 ('serial', UINT)] # is following

class ResurrectionMenu(Packet):
    """
        action: 0 server, 1 resurrect, 2 ghost
    """
    __slots__ = Packet.__slots__
    p_id = 0x2c
    p_type = P_BOTH

    _datagram = [('action', BYTE)]

class RemoveGroup(Packet):
    """
        @deprecated: unneccessary.
        target = serial -> Removed from Group.
    """
    __slots__ = Packet.__slots__
    p_id = 0x39
    p_type = P_BOTH

    _datagram = [('serial', UINT),
                 ('target', UINT)]

class SendSkills(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x1c
    p_type = P_SERVER

    _datagram = [('type', BYTE)]

    def unpack(self):
        self.read_datagram(self._datagram)
        _skill_datagram = [('id', USHORT),
                           ('value', USHORT),
                           ('rawvalue', USHORT),
                           ('lock', BYTE)]
        if self.values['type'] in [0x02, 0xDF]:
            _skill_datagram += [('cap', USHORT)]
        self.values['skills'] = {}
        while len(self._data) > 2:
            skill = {}
            self.read_datagram(_skill_datagram, skill)
            self.values['skills'][skill['id']] = skill
        # skip the terminator.
        return self

    def serialize(self):
        self.begin()

        self.write_datagram(self._datagram)

        return self.finish()


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
    GeneralInformation.p_id: GeneralInformation,
    MoveRequest.p_id: MoveRequest,
    MoveAck.p_id: MoveAck, # resync!
    TalkRequest.p_id: TalkRequest,
    UnicodeTalkRequest.p_id: UnicodeTalkRequest,
    }

client_parsers = {
    }

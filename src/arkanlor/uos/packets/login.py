# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Packets for Login et al.

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
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets
from arkanlor.uos.packet import UOPacket as Packet
from arkanlor.uos.const import LoginDeniedReason
from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP

class LoginComplete(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x55 # the packet id is the first byte in the packet. important for writing packets.
    p_type = P_BOTH # who sends this packets?
    _datagram = []

    def __unicode__(self):
        return "Login Complete"

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

class ClientVersion(Packet):
    __slots__ = Packet.__slots__
    p_id = 0xbd
    p_type = P_BOTH # note server and client differs.
    _datagram = [ ('version', CSTRING) ]

    def __unicode__(self):
        return u'Client Version %s' % (self.values.get('version', None))

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
            ('dir', BYTE),
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

class LoginDenied(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x82
    p_type = P_SERVER
    _datagram = [('reason', BYTE, None, LoginDeniedReason.CommunicationProblem), ]




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

    def _serialize(self):
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

    def _serialize(self):
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

class CreateCharacter(Packet):
    __slots__ = Packet.__slots__
    p_id = 0x00
    p_size = 104
    p_type = P_SERVER
    _datagram = [
            ('pattern1', UINT, None, 0xedededed),
            ('pattern2', UINT, None, 0xffffffff),
            ('pattern3', BYTE),
            ('name', FIXSTRING, 30),
            (0, USHORT),
            ('flag', UINT),
            (1, UINT),
            ('logincount', UINT),
            ('profession', BYTE),
            (2, FIXSTRING, 15),
            ('sex', BYTE),
            ('str', BYTE),
            ('dex', BYTE),
            ('int', BYTE),
            ('skill1', BYTE),
            ('skill1_value', BYTE),
            ('skill2', BYTE),
            ('skill2_value', BYTE),
            ('skill3', BYTE),
            ('skill3_value', BYTE),
            ('color', USHORT),
            ('hair_style', USHORT),
            ('hair_color', USHORT),
            ('facial_hair', USHORT),
            ('location', USHORT),
            (3, USHORT),
            ('slot', USHORT),
            ('client_ip', IPV4),
            ('shirt_color', USHORT),
            ('pants_color', USHORT),
                 ]

class ClientSpy(Packet):
    """ historical packet about client information """
    p_id = 0xa4
    p_type = P_CLIENT
    _datagram = [('data', FIXSTRING, 148)]

    def __unicode__(self):
        return u"I spy %s" % (self.values.get('data'),)

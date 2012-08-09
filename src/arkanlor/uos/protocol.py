# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Unit Description

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
from twisted.internet.protocol import Protocol
import struct  #@UnresolvedImport
from arkanlor.uos.packet_io import packet_lengths

class UOProtocolException(Exception):
    pass

class UOS(Protocol):
    """
        Server Side Protocol.
    """

    def __init__(self, factory):
        self.factory = factory
        self.initialized = False

    def connectionMade(self):
        self.factory.num_connections += 1
        Protocol.connectionMade(self)
        #self.transport.write(struct.pack('>I', self.__seed))
        self._input = ''

    def connectionLost(self, reason):
        self.factory.num_connections -= 1

    def dataReceived(self, data):
        if not self.initialized:
            encryption = data[:4]
            print "Client connects, encryption-key: %s" % ('-'.join([hex(ord(i)) for i in encryption]))
            data = data[4:]
            self.initialized = True
        self._input += data
        while True:
            packet = self._packet_from_buffer()
            if packet is None: break
            self.on_packet(packet)

    def send(self, data):
        self.transport.write(data)

    def on_packet(self, packet):
        self.handler(packet)

    def _packet_from_buffer(self):
        if self._input == '':
            return None
        cmd = ord(self._input[0])
        l = packet_lengths[cmd]
        if l == 0xffff:
            raise UOProtocolException("Unsupported packet %s" % hex(cmd))
        if l == 0:
            if len(self._input) < 3: return None
            l = struct.unpack('>H', self._input[1:3])[0]
            if l < 3 or l > 0x8000:
                raise UOProtocolException("Malformed packet %s" % hex(cmd))
            if len(self._input) < l: return None
            x, self._input = self._input[3:l], self._input[l:]
        else:
            if len(self._input) < l: return None
            x, self._input = self._input[1:l], self._input[l:]
        return (cmd, x)

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
import struct, re  #@UnresolvedImport
from django.http import HttpResponse, HttpResponseNotAllowed, \
    HttpResponseForbidden
from django.test.client import RequestFactory, ClientHandler, Client
from arkanlor.ced.packets import server_parsers, ProtocolVersion, ServerState
from arkanlor.utils import hexprint

class CEDProtocolException(Exception):
    pass

class CED(Protocol):
    """
        Server Side Protocol.
    """

    def __init__(self, factory):
        self.factory = factory
        self.initialized = True

    def connectionMade(self):
        self.factory.num_connections += 1
        Protocol.connectionMade(self)
        self._input = ''
        proto_version = ProtocolVersion().serialize()
        server_state = ServerState().serialize()
        #
        self.send(proto_version)
        #self.send(server_state)

    def connectionLost(self, reason):
        self.factory.num_connections -= 1
        self.quit()

    def dataReceived(self, data):
        self._input += data
        while True:
            packet = self._packet_from_buffer()
            if packet is None: break
            self.on_packet(packet)

    def send(self, data):
        hexprint(data)
        print self.transport.write(data)

    def batch_send(self, datalist):
        step = 20
        i = 0
        for d in xrange(int(len(datalist) / step)):
            self.transport.write(''.join(datalist[step * d: step * d + step]))

    def on_packet(self, packet):
        self.handler(packet)

    def _packet_from_buffer(self):
        #print "Reading packet from buffer"
        if self._input == '':
            return None
        cmd = ord(self._input[0])
        p = server_parsers.get(cmd, None)
        #print "Decoding packet %s" % p
        if not p:
            raise CEDProtocolException('Unknown Packet Type %s' % cmd)
        l = p.p_length
        if l == 0:
            if len(self._input) < 5: return None
            l = struct.unpack('<I', self._input[1:5])[0]
            #if l < 3 or l > 0x8000:
            #    raise CEDProtocolException("Malformed packet %s" % hex(cmd))
            if len(self._input) < l: return None
            x, self._input = self._input[5:l], self._input[l:]
        else:
            if len(self._input) < l: return None
            x, self._input = self._input[1:l], self._input[l:]
        #print "cmd, x, %s, %s" % (cmd, x)
        return (cmd, x)

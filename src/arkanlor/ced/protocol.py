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
from arkanlor.ced.packets import server_parsers, ProtocolVersion, ServerState, \
    packet_reader
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
            data = packet_reader.read_from_buffer(self._input)
            if data is None: break
            self._input, packet = data[0], data[1:]
            self.on_packet(packet)

    def send(self, data):
        #hexprint(data)
        self.transport.write(data)

    def batch_send(self, datalist):
        step = 20
        i = 0
        for d in xrange(int(len(datalist) / step)):
            self.transport.write(''.join(datalist[step * d: step * d + step]))

    def on_packet(self, packet):
        self.handler(packet)

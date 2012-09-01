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
from arkanlor.uos.packet_io import packet_lengths
from django.http import HttpResponse, HttpResponseNotAllowed
from django.test.client import RequestFactory, ClientHandler, Client

class UOProtocolException(Exception):
    pass

class UOS(Protocol):
    """
        Server Side Protocol.
    """

    def __init__(self, factory):
        self.factory = factory
        self.initialized = False
        self.http_handler = None

    def connectionMade(self):
        self.factory.num_connections += 1
        Protocol.connectionMade(self)
        self._input = ''

    def connectionLost(self, reason):
        self.factory.num_connections -= 1
        self.quit()

    def dataReceived(self, data):
        if not self.initialized:
            encryption = data[:4]
            # detect other protocols.
            if encryption == 'GET ':
                header, data = data.split('\r\n', 1)
                method, path, proto = header.split(' ')
                print "http request detected: %s %s" % (method, path)
                # note: return a HttpResponseRedirect here if you disable this mixin.

                # else play webserver:
                environ = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", data))
                conn = self.transport.getHost()
                environ['SERVER_NAME'] = conn.host
                environ['SERVER_PORT'] = conn.port
                # 
                if not self.http_handler:
                    client = Client(**environ)
                    self.http_handler = client
                else:
                    client = self.http_handler
                response = client.get(path) # get a django request.

                # Write our http response and exit.
                self.transport.write('HTTP/1.1 %s' % response.status_code)
                self.transport.write(str(response))
                self.transport.loseConnection()
                return
            elif encryption == 'POST':
                self.transport.write(str(HttpResponseNotAllowed()))
                self.transport.loseConnection()
                return
            elif encryption == chr(0xfe):
                # minecraft status
                print "Minecraft pinged me."
                message = 'NOT minecraft'
                message = ''.join([ '\x00%s' % c for c in message ])
                self.transport.write('\xff\x00\r%sx00\xa7\x000\x00\xa7\x003\x000' % message)
                self.transport.loseConnection()
                return
            # go on.
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

    def batch_send(self, datalist):
        step = 20
        i = 0
        for d in xrange(int(len(datalist) / step)):
            self.transport.write(''.join(datalist[step * d: step * d + step]))

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

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
from arkanlor.uos.packet import packet_lengths
from django.http import HttpResponse, HttpResponseNotAllowed, \
    HttpResponseForbidden
from django.test.client import RequestFactory, ClientHandler, Client
from arkanlor.uos.packets import packet_reader

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
                environ['WORLD'] = self.factory.world
                environ['CLIENTS'] = self.factory.clients
                # 
                if not self.http_handler:
                    client = Client(**environ)
                    self.http_handler = client
                else:
                    client = self.http_handler
                response = client.get(path) # get a django request.

                # Write our http response and exit.
                self.transport.write('HTTP/1.1 %s\r\n' % response.status_code)
                self.transport.write(str(response))
                self.transport.loseConnection()
                return
            elif encryption == 'POST':
                response = HttpResponseForbidden() # or redirect?
                self.transport.write('HTTP/1.1 %s %s\r\n' % (response.status_code, 'read only server'))
                self.transport.write(str(response))
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
            #### PASSED! ####
            elif len(encryption) == 4 and encryption[0] == chr(0xef):
                # new way: client new version.
                self.initialized = True
            else:
                # go on. old way.
                print "Client connects, encryption-key: %s" % ('-'.join([hex(ord(i)) for i in encryption]))
                data = data[4:]
                self.initialized = True
        self._input += data
        while True:
            data = packet_reader.read_from_buffer(self._input)
            if data is None: break
            self._input, packet = data[0], data[1:]
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


# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''

Arkanlor Server Startup Environment.

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''


from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from uos.protocol import UOS
from uos.server import ServedClient

class ArkFactory(Factory):
    num_connections = None
    def __init__(self, *args, **kwargs):
        self.num_connections = 0
        self.clients = {}

    def buildProtocol(self, addr):
        protocol = UOS(self)
        client = ServedClient(protocol)
        self.clients[addr] = client
        return protocol

if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 2597)
    endpoint.listen(ArkFactory())
    print "Arkanlor running."
    reactor.run()#@UndefinedVariable
    print "Arkanlor stopped."

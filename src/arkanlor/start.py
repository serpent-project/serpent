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
#
import sys
sys.path.append("..")

from arkanlor.console import stdio, ConsoleCommandProtocol
from twisted.internet.task import LoopingCall
from arkanlor.boulder.task import BoulderTask
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from arkanlor.uos.protocol import UOS
from arkanlor.uos.server import ServedClient

class ArkFactory(Factory):
    num_connections = None
    def __init__(self, world, *args, **kwargs):
        self.num_connections = 0
        self.world = world
        self.clients = {}

    def buildProtocol(self, addr):
        protocol = UOS(self)
        client = ServedClient(protocol, self.world)
        self.clients[addr] = client
        return protocol

if __name__ == '__main__':
    # build our world.
    boulder = BoulderTask(reactor)
    # run our boulder server.
    lc = LoopingCall(boulder.run)
    lc.start(0.1)
    # run our network server.
    endpoint = TCP4ServerEndpoint(reactor, 2597)
    factory = ArkFactory(boulder)
    endpoint.listen(factory)
    # bind console
    stdio.StandardIO(ConsoleCommandProtocol(factory))
    print "Arkanlor running."
    reactor.run()#@UndefinedVariable
    print "Arkanlor stopped."

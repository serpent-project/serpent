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
import sys, os
sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkanlor.settings")

from arkanlor.console import stdio, ConsoleCommandProtocol
from twisted.internet.task import LoopingCall
from arkanlor.boulder.task import BoulderTask
from twisted.internet.protocol import Factory
from arkanlor.notch.factory import MCFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from arkanlor.uos.protocol import UOS
from arkanlor.uos.server import ServedClient
from arkanlor import settings
from arkanlor.ced.factory import CEDFactory

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

    def loseClient(self, client):
        for key, value in self.clients.items():
            if value == client:
                del self.clients[key]

if __name__ == '__main__':
    # build our world.
    print "Arkanlor starting up..."
    print "Loading Boulder."
    boulder = BoulderTask(reactor)
    # run our boulder server.
    lc = LoopingCall(boulder.run)
    print "Start Ticking..."
    lc.start(settings.ARKANLOR_TICK_SPEED)
    # run our network server.
    ports = settings.UOS_PORT
    if not isinstance(ports, list) and not isinstance(ports, tuple):
        ports = (ports,)
    factory = ArkFactory(boulder)
    for port in ports:
        print "Establishing UOS Server endpoint at port %s" % port
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(factory)

    ############ CED ###############
    ports = settings.CED_PORT
    if not isinstance(ports, list) and not isinstance(ports, tuple):
        ports = (ports,)
    factory = CEDFactory(boulder)
    for port in ports:
        print "Establishing CentrED Server endpoint at port %s" % port
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(factory)
    ######### 
    ports = getattr(settings, 'NOTCH_PORT', [])
    if not isinstance(ports, list) and not isinstance(ports, tuple):
        ports = (ports,)
    factory = MCFactory(boulder)
    for port in ports:
        print "Establishing Minecraft Server endpoint at port %s" % port
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(factory)
    # bind console
    stdio.StandardIO(ConsoleCommandProtocol(factory))
    print "Arkanlor running."
    reactor.run()#@UndefinedVariable
    print "Arkanlor stopped."

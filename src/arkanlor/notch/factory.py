# -*- coding: utf-8 -*-
from twisted.internet.protocol import Factory
from arkanlor.notch.protocol import MC
from arkanlor.notch.server import ServedClientNotch

class MCFactory(Factory):
    num_connections = None
    def __init__(self, world, *args, **kwargs):
        self.num_connections = 0
        self.world = world
        self.clients = {}

    def buildProtocol(self, addr):
        protocol = MC(self)
        client = ServedClientNotch(protocol, self.world)
        self.clients[addr] = client
        return protocol

    def loseClient(self, client):
        for key, value in self.clients.items():
            if value == client:
                del self.clients[key]

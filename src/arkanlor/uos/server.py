# -*- coding: utf-8 -*-
from arkanlor.uos import packets as p
from arkanlor.engines.log import LogEngine
from arkanlor.engines.login import Login
from arkanlor.engines.ping import Ping

class ServedClient:
    def __init__(self, protocol): #
        protocol.handler = self._handle_packet

        self._client = protocol
        self._engines = []
        Ping(self)
        LogEngine(self)
        Login(self)

    def add_engine(self, engine):
        self._engines.append(engine)

    def remove_engine(self, engine):
        self._engines.remove(engine)

    def signal(self, name, *args, **keywords):
        for engine in self._engines:
            if hasattr(engine, name):
                if getattr(engine, name)(*args, **keywords):
                    break

    def _handle_packet(self, packet):
        if packet[0] in p.server_parsers:
            packet = p.server_parsers[packet[0]](packet[1])
            packet.unpack()
            print "< %s" % packet
            self.signal('on_packet', packet)
        else:
            print "Packet unknown:", hex(packet[0])

    def send(self, data):
        if not isinstance(data, basestring):
            print "> %s" % data
            data = data.serialize()
        self._client.send(data)

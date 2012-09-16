# -*- coding: utf-8 -*-
from arkanlor.notch import packets as p
from arkanlor.engines.log import LogEngine
from arkanlor.engines.mcviewer import MCViewer
from arkanlor.dagrm.packet import PacketReader

class ServedClientNotch:
    def __init__(self, protocol, world=None): #
        protocol.handler = self._handle_packet
        protocol.quit = self._quit
        self._world = world
        self._protocol = protocol
        self._engines = []
        LogEngine(self)
        MCViewer(self)

    def add_engine(self, engine):
        self._engines.append(engine)

    def remove_engine(self, engine):
        self._engines.remove(engine)

    def shutdown(self):
        self.signal('on_disconnect')
        for engine in self._engines:
            self.remove_engine(engine)
            del engine

    def _quit(self):
        self.shutdown()
        self._protocol.factory.loseClient(self)

    def signal(self, name, *args, **keywords):
        for engine in self._engines:
            if hasattr(engine, name):
                if getattr(engine, name)(*args, **keywords):
                    break

    def _handle_packet(self, packet):
        try:
            packet = p.packet_reader.init_packet(packet[0], packet[1])
            #print "< %s" % packet
            self.signal('on_packet', packet)
        except PacketReader.UnknownPacketException, e:
            print e
            print "Packet unknown", hex(packet[0])

    def send(self, data):
        if not isinstance(data, basestring):
            #print "> %s" % data
            data = data.serialize()
        self._protocol.send(data)

    def sendall(self, data):
        datalist = []
        for d in data:
            if not isinstance(data, basestring):
                datalist += [d.serialize()]
            else:
                datalist += [d]
        self._protocol.batch_send(datalist)

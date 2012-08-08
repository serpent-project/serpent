
import packets as p
from engines.log import LogEngine
from engines.login import Login

class ServedClient:
    def __init__(self, client): #
        client.handler = self._handle_packet

        self._client = client
        self._engines = []
        LogEngine(self)
        Login(self)

    def add_engine(self, engine):
        self._engines.append(engine)

    def remove_engine(self, engine):
        self._engines.remove(engine)

    def signal(self, name, *args, **keywords):
        for engine in self._engines:
            if hasattr(engine, name):
                getattr(engine, name)(*args, **keywords)

    def _handle_packet(self, packet):
        if packet.cmd in p.server_parsers:
            packet = p.server_parsers[packet.cmd](packet)
            self.signal('on_packet', packet)
        else:
            print "No parser for packet:", hex(packet.cmd)

    def send(self, data):
        self._client.send(data)

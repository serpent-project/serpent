# A simple logging engine
from arkanlor.uos.engine import Engine
from arkanlor.uos import packets as p

class Ping(Engine):

    def on_packet(self, packet):
        if isinstance(packet, p.PingMessage):
            self._ctrl.send(p.PingMessage({'sequence': packet.values['sequence']}))
            return True

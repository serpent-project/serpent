# A simple logging engine
from gemuo.engine import Engine
from arkanlor.uos import packets as p

class Ping(Engine):

    def on_packet(self, packet):
        if isinstance(packet, p.PingMessage):
            self._client.send(p.PingMessage({'sequence': packet.values['sequence']}))
            return True

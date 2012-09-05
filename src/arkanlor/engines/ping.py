# A simple logging engine
from arkanlor.uos.engine import Engine
from arkanlor.uos import packets as p
from arkanlor.uos.packets import general_information as gi

class Ping(Engine):

    def on_packet(self, packet):
        if isinstance(packet, p.PingMessage):
            self._ctrl.send(p.PingMessage({'sequence': packet.values['sequence']}))
            return True
        elif isinstance(packet, gi.ClientLanguage):
            print packet
            return True
        elif isinstance(packet, gi.ClientType):
            print packet
            return True

# A simple logging engine
from arkanlor.uos.engine import Engine

class LogEngine(Engine):
    def on_packet(self, packet):
        print '%s %s: %s' % (hex(packet.p_id),
                           packet.__class__.__name__,
                           unicode(packet))

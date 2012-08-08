# A simple logging engine
from gemuo.engine import Engine
from .. import packets as p

class LogEngine(Engine):

    def on_packet(self, packet):
        print '%s %s: %s' % (packet.p_id, packet.__class__.__name__,
                           unicode(packet))

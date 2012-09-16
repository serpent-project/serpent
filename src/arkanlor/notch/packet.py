# -*- coding: utf-8 -*-
"""
    PacketIO Library for binary packetformats used in UO Protocol.
    Packet tries to define a new-style object packet with complete read/write built in.
    Theoretically this approach should be even optimal,
    however the creation of a dictionary in the packet still needs a bit of horsepower.
    
    The old static approach worked well too, however this packet class allows
    the definition of a standard datagram, enabling most packets to be defined
    with _datagram = [ ( identifier, type ), ( 'name', FIXSTRING, 30 ), ... ]
    
"""
from arkanlor.dagrm import Packet
from arkanlor.dagrm.packet import PacketReader



class MCPacket(Packet):
    # see euclid.py for further optimizations.
    __slots__ = [ 'p_id', 'p_type', 'p_length', '_datagram', '_data', 'values' ]
    p_id = None
    p_length = None

    def finish(self, data=None):
        if data is None:
            data = self._data
        return data

class MCPacketReader(PacketReader):
    __slots__ = PacketReader.__slots__
    minimal_packet_size = 3 # byte + ushort len
    maximal_packet_size = None
    dataflow = '>' # ux
    lengthtype = None # mc does not use packet lengths. its not udp capable.

    class UnsupportedPacketException(PacketReader.MalformedPacketException):
        pass

    def read_from_buffer(self, buffer):
        """
            Always eats the whole buffer, if plength is unknown.
            
        """
        if buffer == '':
            return None
        cmd = ord(buffer[0])
        p = self.packet_set.get(cmd, None)
        if not p:
            raise PacketReader.UnknownPacketException('Unknown Packet Type %s' % cmd)
        try:
            l = int(p.p_length)
        except:
            l = None
        if l is None: # "dynamic" packet.
            return ('', cmd, buffer[1:])
        else: # fixed size packet.
            if len(buffer) < l: return None
            packet_data, buffer = buffer[1:l], buffer[l:]
        return (buffer, cmd, packet_data)

# -*- coding: utf-8 -*-

"""
    This engine maintains control over the players character.
"""
No parser for packet: 0x34
No parser for packet: 0xbd
No parser for packet: 0xbf
No parser for packet: 0x9
No parser for packet: 0x73
No parser for packet: 0x6

class CharControl(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

    def on_packet(self, packet):
        if isinstance(packet, p.GetPlayerStatus):
            #@todo: start a cascade getting the info for a specific serial.
            self._client.send(p.StatusBarInfo.PacketWriter())

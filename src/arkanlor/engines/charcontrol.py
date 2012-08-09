# -*- coding: utf-8 -*-

"""
    This engine maintains control over the players character.
"""
from gemuo.engine import Engine
from arkanlor.uos import packets as p

class CharControl(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)

    def on_packet(self, packet):
        if isinstance(packet, p.GetPlayerStatus):
            #@todo: start a cascade getting the info for a specific serial.
            self._client.send(p.StatusBarInfo().updated(
                                    status_flag=0x01,
                                    name='You',
                                    hp=100,
                                    maxhp=100,
                                    str=100,
                                    dex=100,
                                    int=100,
                                    stam=100,
                                    maxstam=100,
                                    mana=100,
                                    maxmana=100,
                                    gold=1,
                                    ar=1,
                                    weight=1,
                                    maxweight=1,
                                    race=1,
                                    ))

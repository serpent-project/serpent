# -*- coding: utf-8 -*-

from gemuo.engine import Engine
from arkanlor.uos import packets as p
import charcontrol

GAME_ENGINES = [charcontrol.CharControl]

class Login(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self.servers = [ {'name': 'Weltenfall'}, {'name': 'Local'}, {'name': 'And another'}]

    def on_packet(self, packet):
        if isinstance(packet, p.AccountLogin):
            self._client.send(p.ServerList({'servers': self.servers }))
        elif isinstance(packet, p.SelectServer):
            #self._client.send(p.LoginComplete())
            # > redirect.0x8c
            # < postlogin
            # > features 0xb9
            # > charlist 0xa9
            # < select char
            self._client.send(p.CharacterList({'characters':
                                                 [{'name': 'Test1'},
                                                  {'name': 'Test2'}, ]}
                                              ))
        #elif isinstance(packet, p.PlayCharacter):
        #    pass #(should be followed by clientversion)
        #elif isinstance(packet, p.ClientVersion):
        #    #??? 
        elif isinstance(packet, p.GameLogin):
            self._client.send(p.ServerList({'servers': self.servers }))

        elif isinstance(packet, p.LoginCharacter):
            # put in the game connection here.
            self._client.send(p.LoginConfirm({
                                        'serial': 12345,
                                        'body': 180,
                                        'x': 1000,
                                        'y': 1000,
                                        'z': 10,
                                        'direction': 0,
                                        'map_width': 2000,
                                        'map_height': 2000,
                                        }
                                ))
            for engine in GAME_ENGINES:
                # initialize character control.
                engine(self._client)
        #elif isinstance(packet, p.ClientVersion):
        #    # note: if the client does not send this, we need a timer.
        #    # otherwise the login stays on.
        #    self._success()

        #elif isinstance(packet, p.PlayServer):
        #elif isinstance(packet, p.Relay):
        #elif isinstance(packet, p.CharacterList):

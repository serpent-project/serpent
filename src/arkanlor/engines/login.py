# -*- coding: utf-8 -*-

from arkanlor.uos.engine import Engine
from arkanlor.uos import packets as p
import charcontrol
import mapclient

GAME_ENGINES = []

FEATURES_T2A = 0x01
FEATURES_RENAISSANCE = 0x02
FEATURES_3DDAWN = 0x04
FEATURES_LBR = 0x08
FEATURES_AOS = 0x10
FEATURES_6CHARS = 0x20
FEATURES_SE = 0x40
FEATURES_ML = 0x80

FEATURES_ARKANLOR = FEATURES_T2A + FEATURES_RENAISSANCE + FEATURES_3DDAWN + FEATURES_SE + FEATURES_ML

class Login(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)
        self.servers = [ {'name': 'Weltenfall'}, {'name': 'Local'}, {'name': 'And another'}]

    def on_packet(self, packet):
        if isinstance(packet, p.AccountLogin):
            self._ctrl.send(p.ServerList({'servers': self.servers }))
        elif isinstance(packet, p.SelectServer):
            #self._client.send(p.LoginComplete())
            # > redirect.0x8c
            # < postlogin
            # > features 0xb9
            self._ctrl.send(p.Features({'bitflag':FEATURES_ARKANLOR}))
            # > charlist 0xa9
            # < select char
            self._ctrl.send(p.CharacterList({'characters':
                                                 [{'name': 'Test1'},
                                                  {'name': 'Test2'}, ]}
                                              ))
        #elif isinstance(packet, p.PlayCharacter):
        #    pass #(should be followed by clientversion)
        #elif isinstance(packet, p.ClientVersion):
        #    #??? 
        elif isinstance(packet, p.GameLogin):
            self._ctrl.send(p.ServerList({'servers': self.servers }))

        elif isinstance(packet, p.LoginCharacter):
            # authentication, logindenied etc?
            # every client needs a map
            map = mapclient.MapClient(self._ctrl)
            # and an entity to control its character
            charcontrol.CharControl(self._ctrl, map)
            # put in the game connection here.            
            for engine in GAME_ENGINES:
                # initialize other engines.
                engine(self._ctrl)
            self._ctrl.signal('on_logging_in', charname=packet.values.get('name'))
            self._success()
        #elif isinstance(packet, p.ClientVersion):
        #    # note: if the client does not send this, we need a timer.
        #    # otherwise the login stays on.
        #    self._success()

        #elif isinstance(packet, p.PlayServer):
        #elif isinstance(packet, p.Relay):
        #elif isinstance(packet, p.CharacterList):

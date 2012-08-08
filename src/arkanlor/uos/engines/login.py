from gemuo.engine import Engine
from .. import data
from .. import packets as p
import charcontrol

GAME_ENGINES = [charcontrol.CharControl]

class Login(Engine):
    def __init__(self, client):
        Engine.__init__(self, client)
        self.servers = [ data.Server(name='Weltenfall', index=0),
                         data.Server(name='Arkanlor', index=1)]

    def on_packet(self, packet):
        if isinstance(packet, p.AccountLogin):
            self._client.send(p.ServerList.PacketWriter(self.servers))
        elif isinstance(packet, p.SelectServer):
            #self._client.send(p.LoginComplete.PacketWriter())
            self._client.send(p.CharacterList.PacketWriter([data.Character(name='Test'),
                                                            data.Character(name='Test2'), ]))
        #elif isinstance(packet, p.PlayCharacter):
        #    pass #(should be followed by clientversion)
        #elif isinstance(packet, p.ClientVersion):
        #    #??? 
        elif isinstance(packet, p.GameLogin):
            self._client.send(p.ServerList.PacketWriter(self.servers))

        elif isinstance(packet, p.LoginCharacter):
            # put in the game connection here.
            self._client.send(p.LoginConfirm.PacketWriter(
                                        serial=12345,
                                        body=180,
                                        x=1000,
                                        y=1000,
                                        z=10,
                                        direction=0,
                                        map_width=2000,
                                        map_height=2000,
                                ))
            for engine in GAME_ENGINES:
                # initialize character control.
                engine(self._client)
        elif isinstance(packet, p.ClientVersion):
            # note: if the client does not send this, we need a timer.
            # otherwise the login stays on.
            self._success()

        #elif isinstance(packet, p.PlayServer):
        #elif isinstance(packet, p.Relay):
        #elif isinstance(packet, p.CharacterList):

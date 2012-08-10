# -*- coding: utf-8 -*-

"""
    This engine maintains control over the players character.
"""
from arkanlor.uos.engine import Engine#@UnresolvedImport
from arkanlor.uos import packets as p

class CharControl(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)

    def on_login(self, charname):
        # make the world aware that this engine is controlling our character.

        # security checks may happen here.
        #self.factory.world.register_engine(self, account)
        # create our gm dragon
        mobile = self._ctrl._world.gamestate.gm_body(charname, 1318, 1076, 1)
        self._ctrl.send(p.LoginConfirm({
                                        'serial': mobile.serial,
                                        'body': mobile.body,
                                        'x': mobile.x,
                                        'y': mobile.y,
                                        'z': mobile.z,
                                        'direction': mobile.dir,
                                        }
                                ))
        self.send(p.GIMapChange())
        self.send(p.LoginComplete())
        self.send(p.GIMapChange())
        self.mobile = mobile

    def on_packet(self, packet):
        if isinstance(packet, p.MoveRequest):
            self.send(p.MoveAck({'seq': packet.values.get('seq')}))
        elif isinstance(packet, p.GetPlayerStatus):
            #@todo: start a cascade getting the info for a specific serial.
            m = self.mobile
            self.send(p.StatusBarInfo().updated(
                                    serial=m.serial,
                                    status_flag=0x01,
                                    name=m.name,
                                    hp=m.hp,
                                    maxhp=m.maxhp,
                                    str=m.str,
                                    dex=m.dex,
                                    int=m.int,
                                    stam=m.stam,
                                    maxstam=m.maxstam,
                                    mana=m.mana,
                                    maxmana=m.maxmana,
                                    gold=1,
                                    ar=m.ar,
                                    weight=1,
                                    maxweight=1,
                                    race=1,
                                    ))

            self.send(p.UpdatePlayer(
                        { 'serial': m.serial,
                          'body': m.body,
                          'x': m.x,
                          'y': m.y,
                          'z': m.z,
                          'direction': m.dir,
                          'color': m.color,
                          'flag': 0x0,
                          'highlight': 0x0,
                          }
                        ))
            self.send(p.Teleport(
                        { 'serial': m.serial,
                          'body': m.body,
                          'x': m.x,
                          'y': m.y,
                          'z': m.z,
                          'direction': m.dir,
                          'color': m.color,
                          'flag': 0x0, }
                                 ))

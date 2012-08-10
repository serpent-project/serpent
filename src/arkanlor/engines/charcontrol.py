# -*- coding: utf-8 -*-

"""
    This engine maintains control over the players character.
"""
from arkanlor.uos.engine import Engine#@UnresolvedImport
from arkanlor.uos import packets as p
from arkanlor.uos import const

MOTD = 'You logged in. Arkanlor V%s' % ('0.1',)

class CharControl(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)

    def on_login(self, charname):
        # make the world aware that this engine is controlling our character.

        # security checks may happen here.
        #self.factory.world.register_engine(self, account)
        # create our gm dragon
        m = self._ctrl._world.gamestate.gm_body(charname, 1318, 1076, 1)
        self._ctrl.send(p.LoginConfirm({
                                        'serial': m.serial,
                                        'body': m.body,
                                        'x': m.x,
                                        'y': m.y,
                                        'z': m.z,
                                        'direction': m.dir,
                                        }
                                ))
        self.send(p.GIMapChange())
        self.send(p.LoginComplete())
        self.mobile = m

    def on_packet(self, packet):
        if isinstance(packet, p.MoveRequest):
            self.send(p.MoveAck({'seq': packet.values.get('seq')}))
        elif isinstance(packet, p.ClientVersion):
            # usually sent at beginning.
            m = self.mobile
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
            # Send our motd.
            self.send(p.SendSpeech({'ttype': const.TTYPE_SYS_CORNER,
                                'serial': 0xffff,
                                'message': MOTD }))
        elif isinstance(packet, p.TalkRequest) or isinstance(packet, p.UnicodeTalkRequest):
            self.send(p.SendSpeech({'name': self.mobile.name,
                                    'ttype': packet.values['ttype'],
                                    'color': packet.values['color'],
                                    'font': packet.values['font'],
                                    'serial': self.mobile.serial,
                                    'message': packet.values.get('message', '').replace('\0', '')
                                    }))
        elif isinstance(packet, p.GetPlayerStatus):
            #@todo: start a cascade getting the info for a specific serial.
            m = self.mobile
            self.send(p.StatusBarInfo().updated(
                                    serial=m.serial,
                                    status_flag=0x04,
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


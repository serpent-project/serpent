# -*- coding: utf-8 -*-

"""
    This engine maintains control over the players character.
"""
from arkanlor.uos.engine import Engine#@UnresolvedImport
from arkanlor.uos import packets as p
from arkanlor.uos import const
from arkanlor import settings

class CharControl(Engine):
    def __init__(self, controller, map):
        Engine.__init__(self, controller)
        self.map = map

    def sysmessage(self, message):
        self.send(p.SendSpeech({'ttype': const.TTYPE_SYS_CORNER,
                                'serial': 0xffff,
                                'message': message }))

    def on_logging_in(self, charname):
        # make the world aware that this engine is controlling our character.

        # security checks may happen here.
        #self.factory.world.register_engine(self, account)
        # create our gm dragon
        m = self._ctrl._world.gamestate.gm_body(charname, 390, 3770, 1)
        self._ctrl.send(p.LoginConfirm({
                                        'serial': m.id,
                                        'body': m.body,
                                        'x': m.x,
                                        'y': m.y,
                                        'z': m.z,
                                        'direction': m.dir,
                                        }
                                ))
        self._ctrl.signal('on_login', charname, m)
        return True # stop cascade here.

    def on_login(self, user, mobile):
        self.user = user
        self.mobile = mobile
        self.send(p.LoginComplete())


    def on_packet(self, packet):
        if isinstance(packet, p.MoveRequest):
            self.send(p.MoveAck({'seq': packet.values.get('seq')}))
        elif isinstance(packet, p.ClientVersion):
            # usually sent at beginning.
            m = self.mobile
            self.send(p.UpdatePlayer(
                        { 'serial': m.id,
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
                        { 'serial': m.id,
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
                                'message': settings.VERSIONSTRING }))
        elif isinstance(packet, p.TalkRequest) or isinstance(packet, p.UnicodeTalkRequest):
            self.send(p.SendSpeech({'name': self.mobile.name,
                                    'ttype': packet.values['ttype'],
                                    'color': packet.values['color'],
                                    'font': packet.values['font'],
                                    'serial': self.mobile.id,
                                    'message': packet.values.get('message', '').replace('\0', '')
                                    }))
        elif isinstance(packet, p.GetPlayerStatus):
            #@todo: start a cascade getting the info for a specific serial.
            m = self.mobile
            self.send(p.StatusBarInfo().updated(
                                    serial=m.id,
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


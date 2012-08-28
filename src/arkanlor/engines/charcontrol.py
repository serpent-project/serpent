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

    def identify(self, callback):
        # build my mobile data.
        s = 'Name: %s, x: %x, y: %s, z: %s' % (self.mobile.name,
                                               self.mobile.x,
                                               self.mobile.y,
                                               self.mobile.z)
        try:
            callback(s)
        except:
            print "Identify called with faulty callback."

    def sysmessage(self, message, color=0x24, font=0x4):
        self.send(p.SendSpeech({'ttype': const.TTYPE_SYS_CORNER,
                                'color': color,
                                'font': font,
                                'serial': 0xffff,
                                'message': message }))

    def on_logging_in(self, charname):
        # make the world aware that this engine is controlling our character.

        # security checks may happen here.
        #self.factory.world.register_engine(self, account)
        # create our gm dragon
        lp = settings.LOGIN_POINTS['default']
        m = self._ctrl._world.gamestate.gm_body(charname, lp['x'], lp['y'], lp['z'])
        self.shadow = self._ctrl._world.gamestate.gm_body('shadow of ' + charname, lp['x'], lp['y'], lp['z'])
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
        # send our shadow
        if self.shadow:
            shadow = self.shadow.packet_info()
            shadow['serial'] = self.shadow.id
            self.send(p.ShowMobile(shadow))


    def on_packet(self, packet):
        if isinstance(packet, p.MoveRequest):
            walkcode, self.mobile = self._ctrl._world.gamestate.try_move(self.mobile,
                                                                         packet.values.get('dir'))
            if not walkcode:
                self.send(p.MoveAck({'seq': packet.values.get('seq')}))
                if self.shadow:
                    shadow = self.mobile.packet_info()
                    shadow['serial'] = self.shadow.id
                    self.send(p.UpdateMobile(shadow))
            elif walkcode:
                self.send(p.MoveReject({'seq': packet.values.get('seq'),
                                        'x': self.mobile.x,
                                        'y': self.mobile.y,
                                        'z': self.mobile.z,
                                        'dir': self.mobile.dir}))
            # check my range
            if self.mobile.range_to_last_pos() > 12:
                self._ctrl.signal('send_mobile_area', self.mobile)
                self.mobile.remember_last_pos()
        elif isinstance(packet, p.ClientVersion):
            # usually sent at beginning.
            m = self.mobile
            self.send(p.UpdatePlayer(
                        { 'serial': m.id,
                          'body': m.body,
                          'x': m.x,
                          'y': m.y,
                          'z': m.z,
                          'dir': m.dir,
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
                          'dir': m.dir,
                          'color': m.color,
                          'flag': 0x0, }
                                 ))
            # Send our motd.
            self.sysmessage(settings.VERSIONSTRING)
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


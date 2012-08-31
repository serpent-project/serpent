# -*- coding: utf-8 -*-

"""
    This engine maintains control over the players character.
"""
from arkanlor.uos.engine import Engine#@UnresolvedImport
from arkanlor.uos import packets as p
from arkanlor.uos import const
from arkanlor import settings
from arkanlor.boulder.dynamics.agent import Agent

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

    def send_object(self, obj, update_only=False):
        return self.map.send_object(obj, update_only)

    def get_serial(self, obj, notify=False):
        return self.map.get_serial(obj, notify)

    def on_disconnect(self):
        self.mobile._db.logged_in = False
        self.mobile._db_update()

    def on_logging_in(self, account, char):
        # make the world aware that this engine is controlling our character.

        # security checks may happen here.
        #self.factory.world.register_engine(self, account)
        # create our gm dragon
        m = self._ctrl._world.gamestate.get_agent(char, socket=self)
        self._ctrl.send(p.LoginConfirm({
                                        'serial': self.map.get_serial(m),
                                        'body': m.body,
                                        'x': m.x,
                                        'y': m.y,
                                        'z': m.z,
                                        'dir': m.dir,
                                        }
                                ))
        self._ctrl.signal('on_login', account, m)
        return True # stop cascade here.

    def on_login(self, user, mobile):
        self.user = user
        self.mobile = mobile
        self.send(p.LoginComplete())

    def on_packet(self, packet):
        if isinstance(packet, p.MoveRequest):
            if self.mobile.walk(packet.values.get('dir')):
                self.send(p.MoveAck({'seq': packet.values.get('seq')}))
            else:
                self.send(p.MoveReject({'seq': packet.values.get('seq'),
                                        'x': self.mobile.x,
                                        'y': self.mobile.y,
                                        'z': self.mobile.z,
                                        'dir': self.mobile.dir}))
            # check my range
            if self.mobile.range_to_last_pos() > 8:
                self._ctrl.signal('send_mobile_area', self.mobile)
                self.mobile.remember_last_pos()
        elif isinstance(packet, p.ClientVersion):
            # usually sent at beginning.
            m = self.mobile
            self.send(p.UpdatePlayer(
                        { 'serial': self.map.get_serial(m),
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
                        { 'serial': self.map.get_serial(m),
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
                                    serial=self.map.get_serial(m),
                                    status_flag=0x04,
                                    name=str(m.name),
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


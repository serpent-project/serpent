# -*- coding: utf-8 -*-

from arkanlor.uos.engine import Engine
from arkanlor.uos import packets as p
from arkanlor.boulder.models import PlayerMobile
from arkanlor import settings
import charcontrol
import mapclient
from arkanlor.uos.const import LoginDeniedReason

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

CLIENT_DIALECT_CLASSIC = 1 # the classic protocol. incapable of multiitems.
CLIENT_DIALECT_IRIS = 2
CLIENT_DIALECT_NEW = 3 # sa and above, using clientnewversion.
CLIENT_DIALECT_FLUORESCENCE = 4

class Login(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)
        self.servers = settings.LOGIN_SERVERS
        self.account = None
        self.client_dialect = CLIENT_DIALECT_CLASSIC

    def send_character_list(self, account):
        characters = PlayerMobile.objects.filter(owner=self.account)
        characters = [ {'name': str(char.name)} for char in characters ]
        self._ctrl.send(p.CharacterList({'characters': characters}))

    def on_packet(self, packet):
        if isinstance(packet, p.AccountLogin):
            # authenticate.
            self.account = self._ctrl._world.authenticate(
                                    packet.values.get('username', None),
                                    packet.values.get('password', None))
            if self.account:
                self._ctrl.send(p.ServerList({'servers': self.servers }))
            else:
                #self._ctrl.send(p.LoginDeclined())
                self.send(p.LoginDenied({'reason': LoginDeniedReason.Incorrect }))
        elif isinstance(packet, p.CreateCharacter):
            if self.account:
                lp = settings.LOGIN_POINTS['default']
                mobile = self._ctrl._world.gamestate.new_body(
                                    PlayerMobile,
                                    packet.values.get('name'),
                                    lp['x'], lp['y'], lp['z'],
                                    dont_persist=True)
                mobile.str = packet.values.get('str')
                mobile.dex = packet.values.get('dex')
                mobile.int = packet.values.get('int')
                mobile.color = packet.values.get('color')
                mobile._db.owner = self.account
                mobile._db_update()
                self.send_character_list(self.account)
            else:
                self.send(p.LoginDenied())
        elif isinstance(packet, p.SelectServer):
            if self.account:
                # if this is not true, select server was tried to be sent before account login.
                # disconnect and log.
                # > redirect.0x8c
                # < postlogin
                # > features 0xb9

                # only for classic client, iris:
                if self.client_dialect in [CLIENT_DIALECT_CLASSIC, CLIENT_DIALECT_IRIS]:
                    self._ctrl.send(p.Features({'bitflag':FEATURES_ARKANLOR}))
                # > charlist 0xa9
                # < select char
                self.send_character_list(self.account)
            else:
                self.send(p.LoginDenied())
        #elif isinstance(packet, p.PlayCharacter):
        #    pass #(should be followed by clientversion)
        #elif isinstance(packet, p.ClientVersion):
        #    #???
        elif isinstance(packet, p.ClientNewVersion):
            # save version information?
            # set client dialect to 7 or up.
            self.client_dialect = CLIENT_DIALECT_NEW
        elif isinstance(packet, p.GameLogin):# or isinstance(packet, p.ClientNewVersion):
            if self.account:
                self._ctrl.send(p.ServerList({'servers': self.servers }))
            else:
                self.send(p.LoginDenied())
                return
        elif isinstance(packet, p.LoginCharacter):
            if not self.account:
                self.send(p.LoginDenied())
                return
            # authentication, logindenied etc?
            # every client needs a map
            map = mapclient.MapClient(self._ctrl)
            # and an entity to control its character
            charcontrol.CharControl(self._ctrl, map)
            # put in the game connection here.            
            for engine in GAME_ENGINES:
                # initialize other engines.
                engine(self._ctrl)
            try:
                char = PlayerMobile.objects.get(
                                            owner=self.account,
                                            name=packet.values.get('name'))
            except PlayerMobile.DoesNotExist, e:
                self.send(p.LoginDenied({'reason': LoginDeniedReason.IGRAuth}))
                return
            self._ctrl.signal('on_logging_in', account=self.account, char=char)
            self._success()
        #elif isinstance(packet, p.ClientVersion):
        #    # note: if the client does not send this, we need a timer.
        #    # otherwise the login stays on.
        #    self._success()

        #elif isinstance(packet, p.PlayServer):
        #elif isinstance(packet, p.Relay):
        #elif isinstance(packet, p.CharacterList):

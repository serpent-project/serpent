# -*- coding: utf-8 -*-

from arkanlor.uos.engine import Engine
from arkanlor.ced import packets as p
from arkanlor.boulder.models import PlayerMobile, WorldMapRegion
from arkanlor import settings
from arkanlor.ced.const import LoginStates, AccessLevel, ServerStates
from arkanlor.engines import cedcontrol

GAME_ENGINES = []

class CedLogin(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)
        self.account = None

    def on_packet(self, packet):
        if isinstance(packet, p.LoginRequest):
            print "Login Request from CED %s" % packet.values.get('username', None)
            # authenticate.
            self.account = self._ctrl._world.authenticate(
                                    packet.values.get('username', None),
                                    packet.values.get('password', None))
            if self.account:
                if self.account.is_superuser:
                    access_level = AccessLevel.Admin
                elif self.account.is_active:
                    access_level = AccessLevel.Normal
                else:
                    access_level = AccessLevel.View
                self._ctrl.send(p.LoginResponse({'state': LoginStates.OK,
                                        'access_level': access_level ,
                                        # @todo: boulder.boundaries
                                         'map_width': 64 * 64,
                                         'map_height': 64 * 64 }))
                # also send client list with compressed packet.
                # send client connected to all ced clients.
                # send clientpospacket to clients lastpos.
                # this is already a successful login.

                # map = mapclient.MapClient(self._ctrl)
                cedcontrol.CedControl(self._ctrl)
                for engine in GAME_ENGINES:
                    # initialize other engines.
                    engine(self._ctrl)
                self._ctrl.signal('on_logging_in', account=self.account, char=None)
                print "CED Account %s logged in" % self.account.username
                return self._success()
            else:
                self.send(p.LoginResponse({'state': LoginStates.InvalidPassword }))
                return


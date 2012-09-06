# -*- coding: utf-8 -*-

from arkanlor.uos.engine import Engine
from arkanlor.ced import packets as p
from arkanlor.boulder.models import PlayerMobile, WorldMapRegion
from arkanlor import settings
from arkanlor.ced.const import LoginStates, AccessLevel, ServerStates

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
                self._ctrl.send(p.LoginResponse({'state': LoginStates.OK,
                                        'access_level': AccessLevel.Admin \
                                             if self.account.is_superuser\
                                             else AccessLevel.View ,
                                         'map_width': 64 * 64,
                                         'map_height': 64 * 64 }))
                # also send client list with compressed packet.
                # send client connected to all ced clients.
                # send clientpospacket to clients lastpos.
                # this is already a successful login.

                # map = mapclient.MapClient(self._ctrl)
                # cedcontrol.CedControl(self._ctrl, map)
                for engine in GAME_ENGINES:
                    # initialize other engines.
                    engine(self._ctrl)
                self._ctrl.signal('on_logging_in', account=self.account, char=None)
                #return self._success()
            else:
                #self._ctrl.send(p.LoginDeclined())
                self.send(p.LoginResponse({'state': LoginStates.InvalidPassword }))
                return
        # Region Management
        if isinstance(packet, p.RegionList):
            # get our regions
            regions_db = WorldMapRegion.objects.filter(owner__isnull=True,
                                          owner=self.account)

            regions = {'count': regions_db.count(),
                       'regions': []}
            for region in regions_db:
                regions['regions'] += [ region.packet_info() ]
            self.send(p.RegionList(regions))

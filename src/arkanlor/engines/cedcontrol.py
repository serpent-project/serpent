# -*- coding: utf-8 -*-

from arkanlor.uos.engine import Engine
from arkanlor.ced import packets as p
from arkanlor.boulder.models import WorldMapRegion
from arkanlor import settings
from arkanlor.ced.const import ModifyRegionStatus, DeleteRegionStatus
from django.db.models import Q
from django.contrib.auth.models import User

class CedControl(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)
        self.account = None

    def get_map(self):
        return self._ctrl._world.gamestate.get_map()
    worldmap = property(get_map)

    def on_logging_in(self, account, char):
        self.account = account

    def on_packet(self, packet):
        ### Administration. Maybe move to other package?
        # Region Management
        if isinstance(packet, p.RegionList):
            # get our regions
            regions_db = WorldMapRegion.objects.filter(
                                          Q(owners__isnull=True) |
                                          Q(owners__exact=self.account),
                                          map=self.worldmap,
                                          )

            regions = {'count': regions_db.count(),
                       'regions': []}
            for region in regions_db:
                regions['regions'] += [ region.packet_info() ]
            self.send(p.RegionList(regions))
        elif isinstance(packet, p.ModifyRegion):
            available_regions = WorldMapRegion.objects.filter(map=self.worldmap,
                                                              owners__exact=self.account)
            status = ModifyRegionStatus.NoOp
            packet_info = {}
            name = packet.values.get('name', '')
            if name:
                # modify or add a region
                try:
                    region = available_regions.get(name=name)
                    region.clear_areas()
                    status = ModifyRegionStatus.Modified
                except WorldMapRegion.DoesNotExist:
                    # set up a new region
                    region = WorldMapRegion(map=self.worldmap,
                                            name=name)
                    region.save()
                    region.owners.add(self.account)
                    status = ModifyRegionStatus.Added
                for area in packet.values['areas']:
                    region.add_area(area)
                packet_info.update(region.packet_info())
            packet_info['status'] = status
            self.send(p.ModifyRegion(packet_info))
        elif isinstance(packet, p.DeleteRegion):
            # delete a region
            available_regions = WorldMapRegion.objects.filter(map=self.worldmap,
                                                              owners__exact=self.account)
            status = DeleteRegionStatus.NotFound
            name = packet.values.get('name', '')
            packet_info = {'name': name}
            if name:
                try:
                    region = available_regions.get(name=name)
                    region.clear_areas()
                    region.delete()
                    status = DeleteRegionStatus.Deleted
                except WorldMapRegion.DoesNotExist:
                    pass
            packet_info['status'] = status
            self.send(p.DeleteRegion(packet_info))
        elif isinstance(packet, p.UserList):
            if self.account.is_staff or self.account.is_superuser:
                users_db = User.objects.all()
                users = []
                for u in users_db:
                    uregions = WorldMapRegion.objects.filter(owners__exact=u).values_list('name', flat=True)
                    d = {'name': u.username,
                         'access_level': 0, # modify user database to be read indirectly.
                         'count': len(uregions),
                         'regions': [{'name': rname} for rname in uregions],
                         }
                    users += [d]
                self.send(p.UserList({'count': len(users), 'users': users}))
            else:
                # cannot see other than yourself.
                self.send(p.UserList({'count': 1, 'users': [{'name': self.account.name,
                                                             'access_level': 0,
                                                             'count': 0
                                                             }]}))
        # p.DeleteUser and p.ModifyUser are ignored for now.

        # 

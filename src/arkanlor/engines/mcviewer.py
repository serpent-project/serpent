# -*- coding: utf-8 -*-
"""
    Engine to talk with the MC protocol
    
"""
from arkanlor.uos.engine import Engine
from arkanlor.notch import packets as p
from arkanlor.boulder.models import WorldMapRegion
from arkanlor import settings
from arkanlor.ced.const import ModifyRegionStatus, DeleteRegionStatus
from django.contrib.auth.models import User
from arkanlor.notch.chunks import chunkify_compressed
from arkanlor.utils import hexprint

def mc2uo(x, y, z):
    return (z, x, y)

def uo2mc(x, y, z):
    return (y, z, x)

# uo2mc(*mc2uo(1,2,3)) = mc2uo(*uo2mc(1,2,3))

class MCViewer(Engine):
    def __init__(self, controller):
        Engine.__init__(self, controller)
        self.account = None

    def get_map_db(self):
        return self._ctrl._world.gamestate.get_map_db()
    worldmap_db = property(get_map_db)

    def get_map(self):
        return self._ctrl._world.gamestate.get_map()
    worldmap = property(get_map)

    def on_logging_in(self, account, char):
        self.account = account

    def on_packet(self, packet):
        ### Administration. Maybe move to other package?
        # Region Management
        if isinstance(packet, p.PingVersion):
            # send quit:
            answer = p.DisconnectServerInfo({'reason': 'Arkanlor'})
            self.send(answer)
            #self._ctrl._quit()
            return self._success()
        elif isinstance(packet, p.Handshake):
            coord = settings.LOGIN_POINTS['default']
            sx, sy, sz = coord['x'], coord['y'], coord['z']
            mb1, mb2, mb3, mb4 = self.worldmap.get_blocks16(sx, sy)
            mx, my, mz = uo2mc(sx, sy, sz)
            data, bitmask, bitmask_add = chunkify_compressed(mb1, mb2, mb3, mb4)
            initial_chunks = {
                        'chunk_x': (mx - mx % 16) / 16,
                        'chunk_z': (mz - mz % 16) / 16,
                        'continuous': False,
                        'bitmask': bitmask,
                        'bitmask_add': bitmask_add,
                        'compressed_size': len(data),
                        'compressed_data': data
                        }
            initial_playerpos = {'x': mx,
                                 'y': my,
                                 'z': mz}
            self.send(p.ChunkData(initial_chunks))
            self.send(p.SpawnPosition(initial_playerpos))
            # look packet.
            self.send(p.PlayerPositionLook(
                            {'x': float(mx),
                             'stance': float(mx),
                             'y': float(my),
                             'z': float(mz),
                             'yaw': 0.0,
                             'pitch': 0.0,
                             'on_ground': True,
                             }))
            #self.send(p.Block(response))

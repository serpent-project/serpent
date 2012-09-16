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
        self.initialized = False
        self.account = None

    def get_map_db(self):
        return self._ctrl._world.gamestate.get_map_db()
    worldmap_db = property(get_map_db)

    def get_map(self):
        return self._ctrl._world.gamestate.get_map()
    worldmap = property(get_map)

    def on_logging_in(self, account, char):
        self.account = account

    def send_chunk_area(self, x, y, full=False):
        # sends chunks in the area of x, y
        # we want to get at least 49 chunks (7x7)
        chunks = []
        for i in xrange(7):
            for j in xrange(7):
                sx = x - ((3 + i) * 16)
                sy = y - ((3 + j) * 16)
                mb1, mb2, mb3, mb4 = self.worldmap.get_blocks16(sx, sy)
                mx, my, mz = uo2mc(sx, sy, 0)
                data, bitmask, bitmask_add = chunkify_compressed(mb1, mb2, mb3, mb4, full)
                chunk = {
                    'chunk_x': (mx - mx % 16) / 16,
                    'chunk_z': (mz - mz % 16) / 16,
                    'continuous': full,
                    'bitmask': bitmask,
                    'bitmask_add': bitmask_add,
                    'compressed_size': len(data),
                    'compressed_data': data,
                    'load': True,
                    }
                chunks += [chunk]
        for chunk in chunks:
            self.send(p.PreChunk(chunk))
            self.send(p.ChunkData(chunk))


    def first_packets(self):
        coord = settings.LOGIN_POINTS['default']
        sx, sy, sz = coord['x'], coord['y'], coord['z']
        mb1, mb2, mb3, mb4 = self.worldmap.get_blocks16(sx, sy)
        mx, my, mz = uo2mc(sx, sy, sz)
        data, bitmask, bitmask_add = chunkify_compressed(mb1, mb2, mb3, mb4, True)
        initial_chunks = {
                    'chunk_x': (mx - mx % 16) / 16,
                    'chunk_z': (mz - mz % 16) / 16,
                    'continuous': True,
                    'bitmask': bitmask,
                    'bitmask_add': bitmask_add,
                    'compressed_size': len(data),
                    'compressed_data': data,
                    'load': True,
                    }
        initial_playerpos = {'x': mx,
                             'y': my,
                             'z': mz}
        #self.send(p.PreChunk(initial_chunks))
        #self.send(p.ChunkData(initial_chunks))
        self.send_chunk_area(sx, sy, False)
        self.send(p.SpawnPosition(initial_playerpos))
        self.send(p.OpenWindow({'id': 0,
                                }))
        self.send(p.EmptyInventory())
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
        self.send(p.Message({'message': '&cWelcome to Arkanlor Test'}))
        #self.send(p.Block(response))

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
            self.send(p.Handshake())
        elif isinstance(packet, p.LoginRequest):
            self.send(p.LoginRequest({'entity_id': 0x123}))
            self.first_packets()


# -*- coding: utf-8 -*-
from uo.tiledata import TileData
from uo.animdata import AnimData

animdatamul = '/home/g4b/Spiele/Alathair/animdata.mul'
tiledatamul = '/home/g4b/Spiele/Alathair/tiledata.mul'

tiledata = TileData( tiledatamul )
animdata = AnimData( animdatamul )

print len(animdata)

for i in xrange(len(tiledata.static_tiledata)):
    if tiledata.static_tiledata[i].flags & 0x01000000:
        print "0x%04x - %s" % (i, tiledata.static_tiledata[i].name)
        print animdata[-i -1].frame_count
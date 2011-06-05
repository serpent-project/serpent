# -*- coding: utf-8 -*-

import re
from struct import unpack, pack, calcsize
from uo.statics import *

uodir = "/home/g4b/Spiele/Alathair"
staidx = "staidx0.mul"
statics = "statics0.mul"

ala_statics = Statics("%s/%s" % (uodir, staidx), "%s/%s" % (uodir, statics) )
my_ala_statics = Statics("%s/%s" % (uodir,staidx + ".ala"), "%s/%s" % (uodir,statics +".ala"))

changes = 0

for x in xrange(2000):
    for y in xrange( my_ala_statics.map_y * 8 ):
        mine = my_ala_statics.get_statics( (x, y) )
        thine = ala_statics.get_statics( (x, y) )
        if mine != thine:
            changes += 1

print changes        

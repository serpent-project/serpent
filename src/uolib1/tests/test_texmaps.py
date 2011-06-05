# -*- coding: utf-8 -*-

import re
from struct import unpack, pack, calcsize
from uo.texmaps import *
import os.path

uodir = "/home/g4b/Spiele/Alathair"
texidx = "Texidx.mul"
texmaps = "Texmaps.mul"

my_ala_texmaps = Texmaps(os.path.join(uodir, texidx), os.path.join(uodir, texmaps) )

for i in xrange(0x4000):
    im = my_ala_texmaps.get_entry(i)
    if im:
        im.save('/home/g4b/tmp/tex/0x%04X.png' % i)

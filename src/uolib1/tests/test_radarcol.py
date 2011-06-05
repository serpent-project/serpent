from uo.radarcol import Radarcol
from uo.map import *
from uo.statics import *
import Image, ImageDraw
import time

if __name__ == '__main__':
    import sys
    if not 'nopsyco' in sys.argv:
        try:
            import psyco
            psyco.full()
        except ImportError:
            pass
    radar = Radarcol( '/home/g4b/Spiele/Alathair/Radarcol.mul' )
    map = MapCacheSingular('/home/g4b/Spiele/Alathair/map0.ala')
    uodir = "/home/g4b/Spiele/Alathair"
    staidx_file = "staidx0.mul"
    statics_file = "statics0.mul"
    
    statics = Statics("%s/%s" % (uodir,staidx_file), "%s/%s" % (uodir,statics_file))
    
    im = radar.get_radar_map(map, statics, 4, lower_right = (1800,1800), height_map = True)
    im.save('/home/g4b/test.png', 'PNG')
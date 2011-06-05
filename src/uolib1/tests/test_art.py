from uo.art import *
from uo.common import PILSurface

art = Art('/home/g4b/Spiele/Alathair/artidx.mul', '/home/g4b/Spiele/Alathair/art.mul')
art.load_all()

#for i in range(0x0, 0x4010):
#    image = art.get_tile( i )
#    if image:
#        try:
#            image.save('/home/g4b/tmp/uotest/%s.png' % i, 'PNG')
#            print "%s.png saved." % i
#        except:
#            print "%s.png had failures" % i


def test_art_tile_redraw():
    p = PILSurface()
    p.load('/home/g4b/tmp/uotest/0x3D6B.png')
    art.get_tile( 0x4000 + 0x3D6B )
    data =  art.artmul.image_to_runtile( p )
    print data
    image = art.artmul.runtile_data( data )
    image.save('/home/g4b/tmp/statictest.png', 'PNG')

def save_tile(maptile_id = 0x0000):
    image = art.get_tile(maptile_id)
    if maptile_id < 0x4000:
        name = "map"
    else:
        name = "static"
    if image:
        image.save('/home/g4b/tmp/%s0x%04X.png' % (name, maptile_id), 'PNG')
        print "tile %s0x%04X.png saved." % (name, maptile_id)
    
def test_map_tile_redraw( tile_id = 0x0000):
    p = PILSurface()
    p.load('/home/g4b/tmp/map0x%04X.png' % tile_id)
    art.get_tile( tile_id )
    data =  art.artmul.image_to_rawtile( p )
    print len(data)
    image = art.artmul.rawtile_data( data )
    image.save('/home/g4b/tmp/maptest.png', 'PNG')

# save_tile()
test_map_tile_redraw()
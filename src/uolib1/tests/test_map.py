from uo.map import MapFile, MapCache, Map
import uo.map
import time

my_map = Map('/home/g4b/Spiele/Alathair/map0.ala')
# my_map.save("/home/g4b/map0.test")
print my_map.get_cell(200, 300)
print my_map.get_cell(300, 200)
print my_map.get_cell(300, 300)
print my_map.get_block(300 / 8, 300 / 8)
# my_map.set_cell(300, 300, (168, -8))
print my_map.get_cell(300, 300)
print my_map.get_block(300 / 8, 300 / 8)
my_new_map = Map(OutputClass = None)
my_new_map.new()
time1 = time.time()
for x in xrange(my_map.map_x):
    for y in xrange(my_map.map_y):
        my_new_map.set_block(x, y, my_map.get_block_raw(x, y))
        # a = my_map.get_block(x, y)
print "done - saving now."
my_new_map.save('/home/g4b/map0.test')
time2 = time.time()
print time2 - time1
# my_map2 = MapFile('/home/g4b/map0.test')
# print my_map2.getCell(300,200)
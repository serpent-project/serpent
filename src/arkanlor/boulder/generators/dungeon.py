# -*- coding: utf-8 -*-
from arkanlor.misc import dungeon
from arkanlor.boulder import models
import numpy

class DungeonGenerator(object):
    def __init__(self, name, width, height,
                      min_rooms=8,
                      max_rooms=12,
                      dungeon_layout='crest',):
        # temporary function to create a dungeon and send back an object list.
        # should mimic everything there is to object lists
        d = dungeon.Dungeon(
                        name,
                        width, height,
                        min_rooms=min_rooms,
                        max_rooms=max_rooms,
                        dungeon_layout=dungeon_layout
                      )
        self._d = d

    def generate_at(self, worldmap, cx, cy, cz=0):
        i = models.ItemMulti(
                            worldmap=worldmap,
                            x=cx,
                            y=cy,
                            z=cz,
                            custom_graphic=0x2000)
        i.save()
        d = self._d
        for x in xrange(d.width):
            for y in xrange(d.height):
                # 0x515: cobblestones.
                # 0x519: paved stones
                # 0x1771 + 11: stones
                # 0x0750: stone bricks
                graphic = None
                c = d.cells[x, y]
                if c == dungeon.NOTHING:
                    graphic = numpy.random.randint(0x1771, 0x1771 + 11)
                if c & dungeon.BLOCKED:
                    pass
                if c & dungeon.ROOM:
                    graphic = 0x519
                if c & dungeon.CORRIDOR:
                    graphic = 0x515
                if c & dungeon.PERIMETER:
                    graphic = 0x0750
                if c & dungeon.ENTRANCE:
                    pass
                if c & dungeon.DOORSPACE:
                    pass

                if graphic:
                    # create our item.
                    # o = Item(self.get_next_free_id(), x1 + x, y1 + y, 0, graphic)
                    i.add_item(x, y, 0, graphic)
        return i

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
        def bulk_store(items):
            print "bulk store %s items" % len(items)
            if not items:
                return []
            # save these items
            for n in range(0, len(items), 100):
                batch = items[n:n + 100]
                print "bulk creating %s items." % len(batch)
                models.ItemMultiAttachment.objects.bulk_create(batch)
            return []

        def multiitem(x, y, z=0):
            i = models.ItemMulti(
                            worldmap=worldmap,
                            x=x,
                            y=y,
                            z=z,
                            custom_graphic=0x2000)
            i.save()
            return i

        def block_no(block):
            return (block - (block % 8)) / 8

        d = self._d
        multi_items = {}
        bx, by = int(numpy.ceil(d.width / 8.0)), int(numpy.ceil(d.height / 8.0))
        for x in xrange(bx):
            for y in xrange(by):
                multi_items[x, y] = multiitem(cx + (x * 8), cy + (y * 8))
        print multi_items
        items = []
        for x in xrange(d.width):
            for y in xrange(d.height):
                bx, by = block_no(x), block_no(y)
                mi = multi_items[bx, by]
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
                    items += [models.ItemMultiAttachment(item_multi=mi,
                                                  x_offset=x % 8,
                                                  y_offset=y % 8,
                                                  z_offset=cz,
                                                  graphic=graphic)
                              ]
        bulk_store(items)


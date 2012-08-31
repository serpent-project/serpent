# -*- coding: utf-8 -*-
#!/usr/bin/env python

# setup project, django
import sys, os

sys.path.append("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkanlor.settings")

# import stuff
from arkanlor.boulder.generators.dungeon import DungeonGenerator
from arkanlor.boulder import models
from arkanlor import settings
##############################################################################

def login_dungeon(m):
    lp = settings.LOGIN_POINTS['default']
    print "Generating Dungeon."
    d = DungeonGenerator('Login',
                        width=50,
                        height=50)
    # place it at login coords
    x, y, z = lp['x'] + 5, lp['y'] + 5, 0
    print "Placing dungeon at %s %s %s" % (x, y, z)
    d.generate_at(m, x, y, z)

##############################################################################
def add_map(worldname=None):
    if worldname:
        try:
            return models.WorldMap.objects.get(name=worldname)
        except models.WorldMap.DoesNotExist:
            print "Adding map %s" % worldname
            m = models.WorldMap(name=worldname)
            m.save()
            return m

def delete_world(worldname=None):
    if worldname:
        print "Deleting world %s" % worldname
    else:
        print "Deleting all worlds."
    models.Item.objects.filter(worldmap__name=worldname).delete()

def main():
    print "Arkanlor Test World Generator"
    delete_world()
    #
    print "Generating World..."
    # create a dungeon near login
    m = add_map('default')
    #login_dungeon(m)
    print "Done."


if __name__ == '__main__':
    main()

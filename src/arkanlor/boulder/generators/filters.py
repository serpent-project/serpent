from arkanlor.boulder.generators.const import UOTiles as uot

class AnyBut:
    def __init__(self, exceptions=[]):
        self.exceptions = exceptions
    def is_it_any(self, tile):
        if not self.exceptions:
            return True
        else:
            return tile not in self.exceptions
Any = AnyBut()

class Stamp(object):
    """
    _layout = [[, , , ],
               [, , , ],
               [, , , ], ]
    """
    _simple_select = None
    def check_rel(self, table, lookup, x=1, y=1):
        l = lookup[x][y]


    def check(self):
        return False

class RectStamp(Stamp):
    _layout = [[Any, Any, Any, ],
               [Any, Any, Any, ],
               [Any, Any, Any, ], ]
    _simple_select = None
    def check(self):
        pass

class DiamondStamp(Stamp):
    _layout = [[None, Any, None, ],
               [Any, Any, Any, ],
               [None, Any, None, ], ]
    _simple_select = None
    def check(self):
        pass

class GrassEat(DiamondStamp):
    _layout = [[None, uot.grass, None],
               [uot.grass, AnyBut(uot.grass), uot.grass],
               [None, uot.grass, None]]
    _simple_select = uot.grass




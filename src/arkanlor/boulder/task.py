# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Unit Description

@author: g4b

LICENSE AND COPYRIGHT NOTICE:

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import time
import gamestate

class BoulderTask(object):
    def __init__(self, reactor, gstate=None):
        self.reactor = reactor # the twisted reactor instance
        self.gamestate = gstate or gamestate.BoulderState('Arkanlor')
        self.time = time.time()

    def run(self):
        # time diff.
        t = time.time()
        diff = t - self.time
        self.time = t
        # 

    def register_engine(self, engine, account, character=None):
        print "Account %s whishes to control character %s" % (account, character)
        # now we would hook the engine which we can send signals to regarding timed events around him.


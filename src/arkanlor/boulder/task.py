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
from Queue import PriorityQueue
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

PRIORITY_LOW = 100
PRIORITY_HIGH = 10

class BoulderTask(object):

    def __init__(self, reactor, gstate=None):
        self.reactor = reactor # the twisted reactor instance
        self.gamestate = gstate or gamestate.BoulderState('Arkanlor', task=self)
        self.time = time.time()
        self.queue = PriorityQueue()

    def enqueue(self, something, priority):
        self.queue.put((priority, something))

    def _run(self, delta):
        # check queue here.
        if delta > settings.ARKANLOR_TICK_LIMIT:
            print "tick speed exceeded: %s" % delta
        else:
            # do my thangs.
            pass

    def run(self):
        # time diff.
        t = time.time()
        diff = t - self.time
        #
        self._run(diff)
        #
        self.time = t
        # 

    def authenticate(self, username, password):
        print "Account %s logs in" % username
        try:
            u = User.objects.get(username=username)
            if check_password(password, u.password):
                return u
            return None
        except User.DoesNotExist:
            # auto creation
            if getattr(settings, 'ARKANLOR_AUTO_REGISTER', False):
                return self.create_account(username, password)
            else:
                return None

    def create_account(self, username, password):
        try:
            u = User.objects.get(username=username)
            if check_password(password, u.password):
                return u
            return None
        except User.DoesNotExist:
            u = User(username=username)
            u.set_password(password)
            u.save()
            return u




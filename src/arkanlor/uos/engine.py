#
#  Engine Class. 
#     g4b: Just rewritten to use different variable names for clarity. 
#  Original by GemUO
#
#  (c) 2005-2010 Max Kellermann <max@duempel.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#

from twisted.internet.defer import Deferred

class Engine:
    def __init__(self, controller):
        self._ctrl = controller
        self._ctrl.add_engine(self)
        self.deferred = Deferred()

    def _signal(self, name, *args, **keywords):
        self._ctrl.signal(name, *args, **keywords)

    def __stop(self):
        self._ctrl.remove_engine(self)

    def _success(self, result=None):
        self.__stop()
        self.deferred.callback(result)

    def _failure(self, fail='Engine failed'):
        self.__stop()
        self.deferred.errback(fail)

    def abort(self):
        """Aborts this engine, does not emit a signal."""
        self.__stop()

    def send(self, something):
        return self._ctrl.send(something)

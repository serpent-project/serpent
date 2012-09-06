# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Extended Datagram Tools

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

from arkanlor.dagrm.packet import DatagramManipulator

class DatagramCountLoop(DatagramManipulator):
    __slots__ = ['count', 'items', 'packets']
    def __init__(self, count, items, Packet):
        self.packets = [Packet]
        self.count = count
        self.items = items
    def packet_read(self, values, data):
        # we use a packet to eat the data count times and copy the values into items
        items = values.get(self.items, [])
        count = values.get(self.count, len(items))
        p = self.packets[0]()
        for x in range(0, count):
            p._data = data
            p.values = {}
            p.unpack()
            items += [p.values]
            data = p._data
        values[self.items] = items
        return values, data

    def packet_write(self, values, data):
        # we use a packet to serialize len(items) times giving items[n] as values.
        # 
        items = values.get(self.items, [])
        count = values.get(self.count, len(items))
        p = self.packets[0]()
        for x in range(0, count):
            p._data = ''
            p.values = items[x]
            # write out packet
            p._serialize()
            data += p._data
        return values, data

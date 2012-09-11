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

class DatagramPacket(DatagramManipulator):
    # writes and reads instance
    __slots__ = ['key', 'dtype']
    def __init__(self, datagram_entry):
        self.key, self.dtype = datagram_entry
    def packet_read(self, values, data, instance=None):
        if instance:
            instance.read_datagram([(self.key, self.dtype)], values)
            return values, instance._data
        return values, data
    def packet_write(self, values, data, instance=None):
        if instance:
            instance.write_datagram([(self.key, self.dtype)], values)
            return values, instance._data
        return values, data

class DatagramSub(DatagramManipulator):
    # writes and reads instance
    __slots__ = ['datagram']
    def __init__(self, datagram):
        self.datagram = datagram
    def packet_read(self, values, data, instance=None):
        if instance:
            instance.read_datagram(self.datagram, values)
            return values, instance._data
        return values, data
    def packet_write(self, values, data, instance=None):
        if instance:
            instance.write_datagram(self.datagram, values)
            return values, instance._data
        return values, data


class DatagramIf(DatagramManipulator):
    """
        executes another datagrammanipulator if comparison of value in key
        returns true.
        executes the else_manipulator if given otherwise.
    """
    def __init__(self, key, comparison, when_true,
                 else_do=None):
        self.key = key
        self.comparison = comparison # e.g. lambda x:
        self.sub_manipulator = when_true
        self.else_manipulator = else_do

    def packet_read(self, values, data, instance=None):
        value = values.get(self.key, None)
        if value is not None:
            if self.comparison(value):
                return self.sub_manipulator.packet_read(values, data, instance)
            else:
                if self.else_manipulator is not None:
                    return self.sub_manipulator.packet_read(values, data, instance)
        return values, data

    def packet_write(self, values, data, instance=None):
        value = values.get(self.key, None)
        if value is not None:
            if self.comparison(value):
                return self.sub_manipulator.packet_write(values, data, instance)
            else:
                if self.else_manipulator is not None:
                    return self.sub_manipulator.packet_write(values, data, instance)
        return values, data

class DatagramCountLoop(DatagramManipulator):
    __slots__ = ['count', 'items', 'packets']
    def __init__(self, count, items, Packet):
        self.packets = [Packet]
        self.count = count
        self.items = items
    def packet_read(self, values, data, instance=None):
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

    def packet_write(self, values, data, instance=None):
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

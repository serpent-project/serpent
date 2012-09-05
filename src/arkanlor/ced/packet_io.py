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
from arkanlor.uos.packet_io import Packet
import struct, string #@UnresolvedImport

class CEDPacket(Packet):
    __slots__ = Packet.__slots__

    def get_flow(self):
        return '<' # seriously ?
    flow = property(get_flow)

    def finish(self, data=None):
        if data is None:
            data = self._data
        if self.p_length == 0:
            if len(data) > 0xf0000000:
                raise Exception, "Packet too large"
            data = data[0] + struct.pack('<I', len(data) + 4) + data[1:]
        else:
            if len(data) != self.p_length:
                print 'pid: %s, expected: %s, got: %s, data: %s' % (
                                        hex(self.p_id), self.p_length,
                                        len(data), repr(data))
                raise Exception, "Invalid packet length"
        return data

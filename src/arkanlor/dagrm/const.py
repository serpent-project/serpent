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

# 1 byte types
BOOLEAN = 0x00
BYTE = 0x01
SBYTE = 0x02
# 2 byte types
SHORT = 0x03
USHORT = 0x04
WORD = USHORT
# 4 byte types
UINT = 0x05
INT = 0x06
CARDINAL = UINT # same thing.
IPV4 = 0x15
# 8 byte types
LONG = 0x08
#IPV6 
# variable types
FIXSTRING = 0xa0
CSTRING = 0xa1
PSTRING = 0xa2
UCSTRING = 0xb1
SPEECHSTRING = 0xc0 # custom string type - not used.
UCS2 = 0xc2 # custom string type with pascaline short length
COUNT = 0xcc # count is a write helper. usage: ('count', COUNT, BYTE, 'items')
FLOAT = 0xf0 # 4 byte float
DOUBLE = 0xfd # 8 byte float
RAW = 0xff # read rest of packet. write out directly.

class DatagramException(Exception):
    pass

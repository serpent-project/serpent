# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
   Quanum Postprocessing.
   taking the outer 8 neighbours, quanum tries to do the same thing as
   original dragon, but tries to guess its borders by itself.
   
   It is named after Quanum Q'nor, the king of all earth dragons.

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
import re
re_bracket = re.compile('\(.+\)')
re_bracket_curly = re.compile('\{.+\}')
re_bracket_square = re.compile('\[.+\]')

def read_file(filename):
    """
        simple reader for quanum definition files.
    """
    fh = open(filename, 'r')
    lines = fh.readlines()
    for line in lines:
        # remove comments.
        line = line.split('#')[0].split('//')[0]
        # remove tailing spaces and make it lower
        line = line.strip().lower()
        # 

class QuanumQnor:
    """
        Main Post Processor
    """
    def __init__(self, directory):
        self.directory = directory
        self._reverse = None
        self.groups = {}

    def apply(self, mapblock, levels=None):
        pass

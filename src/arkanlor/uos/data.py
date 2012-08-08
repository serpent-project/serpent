# -*- coding: utf-8 -*-
'''

    Data Structures.

Copyright (C) 2012 by  Gabor Guzmics, <gab(at)g4b(dot)org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''

from fds import fds

# Create Fake Data Structures for our later datanodes.
# these are just dicts, that allow easier access.

Server = fds(['index', 'name'])
Character = fds(['name', ])

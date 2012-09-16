# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Settings for Arkanlor Server.
    This file is also used for the django part.

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
##############################################################################
import os.path, os
# defining root for our python modules
SETTINGS_DIR = os.path.abspath(os.path.dirname(
                                        os.path.join(os.getcwd(), __file__)))
# defining root for whole project
PROJECT_ROOT = os.path.abspath(os.path.join(SETTINGS_DIR, '../..'))
##############################################################################

DEBUG = True
TEMPLATE_DEBUG = DEBUG
# Path to the directory containing this settings.py file. For Windows, make
# sure to use Unix-style forward slashes, they are automatically translated.
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = '12345'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.abspath(os.path.join(PROJECT_ROOT, 'arkanlor.db')), # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

UOS_PORT = 2598, 2599
CED_PORT = 2597
NOTCH_PORT = None #52597

ROOT_URLCONF = 'arkanlor.urls'

VERSIONSTRING = 'Arkanlor v0.1'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sessions',
    # project
    'arkanlor.boulder',
)

LOGIN_POINTS = {
            'default': {'x': 390,
                        'y': 3770,
                        'z': 20,
                        # more info like map / world?
                        }
                }

ARKANLOR_AUTO_REGISTER = True
ARKANLOR_TICK_SPEED = 0.01 # microticks
ARKANLOR_SERVER_TICK = 0.2 # all server actions are based on this speed.
ARKANLOR_TICK_LIMIT = 0.25 # give warning at this speed incursion and eat time.
# @todo: integrators would improve speed.


# root to default mul files
ARKANLOR_MULS = os.path.join(PROJECT_ROOT, 'muls')
DEFAULT_MAP0 = os.path.join(ARKANLOR_MULS, 'map0.mul')
DEFAULT_MAP0_SIZE = (768 * 8, 512 * 8) # 6144, 4096
try:
    from settings_local import *
except ImportError, e:
    pass

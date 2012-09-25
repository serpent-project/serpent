# -*- coding: utf-8 -*-
from django.conf import settings
from arkanlor.dragons.quanum import QuanumQnor
from arkanlor.dragons.dragon import DragonScripts

try:
    quanum = QuanumQnor(settings.QUANUM_SCRIPT_DIR)
except:
    print "Exception occured. QuanumQnor not initialized."
    quanum = None

try:
    dragon_scripts = DragonScripts(settings.DRAGON_SCRIPT_DIR)
except:
    print "Exception occured. DragonScripts not initialized."
    dragon_scripts = None

# -*- coding: utf-8 -*-
from django.conf import settings
from arkanlor.dragons.quanum import QuanumQnor
from arkanlor.dragons.dragon import DragonScripts

quanum = QuanumQnor(settings.QUANUM_SCRIPT_DIR)
dragon_scripts = DragonScripts(settings.DRAGON_SCRIPT_DIR)

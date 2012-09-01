# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response


def server_status(request, template='boulder/boulder_status.html'):
    world = request.META.get('WORLD', None)
    clients = request.META.get('CLIENTS', None)
    context = {'uos_port': settings.UOS_PORT,
               'world_info': world.gamestate.world_info(),
               }
    return render_to_response(template, context)

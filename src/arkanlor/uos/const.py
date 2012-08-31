# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    UO Constants

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

# ttype list for speech packets
TTYPE_NORMAL = 0x00 # Normal 
TTYPE_SYSTEM = 0x01 #Broadcast/System
TTYPE_EMOTE = 0x02 #Emote 
TTYPE_SYS_CORNER = 0x06 #System/Lower Corner
TTYPE_MSG_CORNER = 0x07 #Message/Corner With Name
TTYPE_WHISPER = 0x08 #Whisper
TTYPE_YELL = 0x09 #Yell
TTYPE_SPELL = 0x0A #Spell
TTYPE_GUILD = 0x0D #Guild Chat
TTYPE_ALLIANCE = 0x0E #Alliance Chat
TTYPE_COMMAND = 0x0F #Command Prompts
TTYPE_ENCODED = 0xC0 #Encoded Commands

class MobileStatus:
    Normal = 0x00
    Unknown = 0x01
    CanAlterPaperdoll = 0x02
    Poisoned = 0x04
    GoldenHealth = 0x08
    Unknown2 = 0x10
    Unknown3 = 0x20
    WarMode = 0x40
    Hidden = 0x80

class LoginDeniedReason:
    Incorrect = 0x00 # Incorrect name/password.
    AlreadyUsed = 0x01 #Someone is already using this account.
    Blocked = 0x02 #Your account has been blocked.
    CredentialsInvalid = 0x03 #Your account credentials are invalid.
    CommunicationProblem = 0x04 #Communication problem.
    IGRLimit = 0x05 #The IGR concurrency limit has been met.
    IGRTimeLimit = 0x06 #The IGR time limit has been met.
    IGRAuth = 0x07 #General IGR authentication failure.

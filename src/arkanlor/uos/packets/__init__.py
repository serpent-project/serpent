# -*- coding: utf-8 -*-

from arkanlor.uos.packets.base import P_CLIENT, P_SERVER, P_BOTH, P_EXP
from arkanlor.dagrm import BYTE, USHORT, UINT, RAW, \
    CSTRING, FIXSTRING, IPV4, BOOLEAN, packet_list, SubPackets
from arkanlor.uos.packets.base import Dummy, NoEncryption, PingMessage
from arkanlor.uos.packets.general_information import \
    AsGI, GeneralInformation, MapChange
from arkanlor.uos.packets.login import \
    AccountLogin, CharacterList, ClientSpy, ClientVersion, \
    CreateCharacter, Features, GameLogin, LoginCharacter, \
    LoginComplete, LoginConfirm, LoginDenied, SelectServer, \
    ServerList
# for now lets be short.
from arkanlor.uos.packets.player import *
from arkanlor.uos.packets.talk import *
from arkanlor.uos.packets.world import *
from arkanlor.uos.packet import UOPacketReader

server_parsers = packet_list(
 NoEncryption,
 Dummy,
 AccountLogin,
 GameLogin,
 SelectServer,
 LoginComplete,
 LoginCharacter,
 PingMessage,
 GetPlayerStatus,
 ClientVersion,
 SingleClick,
 DoubleClick,
 GeneralInformation,
 MoveRequest,
 MoveAck, # resync!
 TalkRequest,
 UnicodeTalkRequest,
 CreateCharacter,)

packet_reader = UOPacketReader(server_parsers)

client_parsers = packet_list()

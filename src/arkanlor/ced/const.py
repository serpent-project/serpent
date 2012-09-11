# -*- coding: utf-8 -*-
"""
    Constants for the CED Protocol
"""
PROTOCOL_VERSION = 6

class LoginStates:
    OK = 0
    InvalidUser = 1
    InvalidPassword = 2
    AlreadyLoggedIn = 3
    NoAccess = 4

class ServerStates:
    Running = 0
    Frozen = 1
    Other = 2

class AccessLevel:
    NoAccess = 0
    View = 1
    Normal = 2
    Admin = 255

class ModifyUserStatus:
    InvalidUsername = 0
    Added = 1
    Modified = 2

class DeleteUserStatus:
    NotFound = 0
    Deleted = 1

class ModifyRegionStatus:
    Added = 0
    Modified = 1
    NoOp = 2 # addition.

class DeleteRegionStatus:
    NotFound = 0
    Deleted = 1

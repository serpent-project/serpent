# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Console

    from twisted demo WebCheckerCommandProtocol,

"""
from twisted.internet import stdio, reactor
from twisted.protocols import basic
from twisted.python import rebuild
from importlib import import_module

class ConsoleCommandProtocol(basic.LineReceiver):
    delimiter = '\n' # unix terminal style newlines. remove this line
                     # for use with Telnet

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.sendLine("Type 'help' for help.")

    def lineReceived(self, line):
        # Ignore blank lines
        if not line: return

        # Parse the command
        commandParts = line.split()
        command = commandParts[0].lower()
        args = commandParts[1:]

        # Dispatch the command to the appropriate method.  Note that all you
        # need to do to implement a new command is add another do_* method.
        try:
            method = getattr(self, 'do_' + command)
        except AttributeError, e:
            self.sendLine('Error: no such command.')
        else:
            try:
                method(*args)
            except Exception, e:
                self.sendLine('Error: ' + str(e))

    def do_help(self, command=None):
        """help [command]: List commands, or show help on the given command"""
        if command:
            self.sendLine(getattr(self, 'do_' + command).__doc__)
        else:
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            self.sendLine("Valid commands: " + " ".join(commands))

    def do_quit(self):
        """quit: Quit this session"""
        self.sendLine('Goodbye.')
        self.transport.loseConnection()

    def do_reload(self, *modules):
        """ try to reload one or more python modules.
            KNOW WHAT YOU ARE DOING!
        """
        self.sendLine('reloading module(s) %s' % ', '.join(modules))
        for m in modules:
            try:
                m_ = import_module(m)
                rebuild.rebuild(m_)
            except Exception, e:
                self.sendLine('reloading module %s threw Exception %s' %
                          (m, e,))
        self.sendLine('reloading complete.')

    def do_list(self):
        """
            List all connected clients to the Server
        """
        self.sendLine('Connected (%s):' % (len(self.factory.clients)))
        for addr in self.factory.clients.keys():
            self.sendLine('-' * 20)
            self.sendLine(str(addr))
            self.factory.clients[addr].signal('identify', self.sendLine)


    def do_say(self, *message):
        """
            Broadcast Message to all connected Clients.
        """
        if not message:
            self.sendLine('Usage: say something')
            return
        message = 'CONSOLE: ' + ' '.join(message)
        for addr in self.factory.clients.keys():
            self.factory.clients[addr].signal('sysmessage', message)

    def connectionLost(self, reason):
        # stop the reactor, only because this is meant to be run in Stdio.
        reactor.stop()


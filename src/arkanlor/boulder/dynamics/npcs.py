from arkanlor.boulder.dynamics.agent import Agent
from arkanlor.boulder.dynamics.base import Mobile

class NPC(object):
    """
        abstract class for npcs
    """
    pass

class SimpleNPC(Mobile, NPC):
    """
        An NPC class which cannot have a socket.
        Scripts will be fired on this class, but it wont receive telemetry
        in any other way.
    """
    pass

class AgentNPC(Agent, NPC):
    pass

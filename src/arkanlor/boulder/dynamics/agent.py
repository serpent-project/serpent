from arkanlor.boulder.dynamics.base import Mobile

class Agent(Mobile):
    """
        defines an agent, a mobile which can have a socket.
        note: this does not say, what the socket really does
        the socket supports the send function, the agent still needs to
        be controlled by some engine.        
    """
    __slots__ = Mobile.__slots__ + ['socket']

    def __init__(self, world, _id, x=None, y=None, z=None, socket=None):
        super(Agent, self).__init__(world, _id, x, y, z)
        self.socket = socket

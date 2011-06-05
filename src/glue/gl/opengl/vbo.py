# -*- coding: utf-8 -*-
"""
    Vertex Buffer Objects
    Vertex Array Buffers
"""
from OpenGL.GL import *
from OpenGL.raw import GL
from OpenGL.arrays import ArrayDatatype as ADT
from OpenGL.raw.GL.constants import GL_COLOR_ARRAY, GL_EDGE_FLAG_ARRAY, \
    GL_TEXTURE_COORD_ARRAY, GL_VERTEX_ARRAY
import numpy

FLOAT32 = numpy.float32

class VirtualBuffer(object):
    """
        Defines an abstract virtual OpenGL Buffer
        handles automatic numpy conversion of lists
    """
    def __init__(self, data, usage,
                 size=None,
                 type=None,
                 stride=None,
                 buffer=None,
                 num_convert=FLOAT32):
        self.size = size
        self.type = type
        self.stride = stride
        self.buffer = buffer or glGenBuffers(1)
        if not isinstance(data, numpy.ndarray):
            data = numpy.array(data, num_convert)
        self.update_data(data, usage)

    def update_data(self, data, usage):
        glBindBuffer(GL_ARRAY_BUFFER_ARB, self.buffer)
        glBufferData(GL_ARRAY_BUFFER_ARB,
                     ADT.arrayByteCount(data),
                     ADT.voidDataPointer(data),
                     usage)

    def __del__(self):
        glDeleteBuffers(1, GL.GLuint(self.buffer))

    def bind(self, size=2,
                    type=FL_FLOAT,
                    stride=0):
        """
            Simply executes glBindBuffer. Subclasses also define the pointer.
        """
        glBindBuffer(GL_ARRAY_BUFFER_ARB, self.buffer)

    def state_bind(self, size=2, type=FL_FLOAT, stride=0):
        """
            should set state and bind.
            simply executes bind here.
        """
        self.bind(size, type, stride)

class ColorBuffer(VirtualBuffer):
    def bind(self, size=None,
                    type=None,
                    stride=0):
        """
            defaults to standard settings
        """
        if self.size and size is None:
            size = self.size
        if self.type and type is None:
            type = self.type
        if self.stride and stride is None:
            stride = self.stride
        super(ColorBuffer, self).bind(size, type, stride)
        glColorPointer(size, type, stride, None)

    def state_bind(self, size=None,
                        type=None,
                        stride=0):
        """
            enables client state colorbuffer array
            and binds the buffer with pointer.
        """
        glEnableClientState(GL_COLOR_ARRAY)
        self.bind(size, type, stride)

class EdgeFlagBuffer(VirtualBuffer):
    def bind(self, size=None, type=None, stride=0):
        """
            For EdgeFlags only stride is important.
        """
        if self.size and size is None:
            size = self.size
        if self.type and type is None:
            type = self.type
        if self.stride and stride is None:
            stride = self.stride
        super(EdgeFlagBuffer, self).bind(size, type, stride)
        glEdgeFlagPointer(stride, None)

    def state_bind(self, size=None,
                        type=None,
                        stride=0):
        """
            enables client state edge flag array
            and binds the buffer with pointer.
        """
        glEnableClientState(GL_EDGE_FLAG_ARRAY)
        self.bind(size, type, stride)

class IndexBuffer(VirtualBuffer):
    def bind(self, size=None, type=None, stride=0):
        """
            IndexBuffers dont need size.
        """
        if self.size and size is None:
            size = self.size
        if self.type and type is None:
            type = self.type
        if self.stride and stride is None:
            stride = self.stride
        super(IndexBuffer, self).bind(size, type, stride)
        glIndexPointer(type, stride, None)

    def state_bind(self, size=None,
                        type=None,
                        stride=0):
        """
            enables client state index array
            and binds the buffer with pointer.
        """
        glEnableClientState(GL_INDEX_ARRAY)
        self.bind(size, type, stride)

class NormalBuffer(VirtualBuffer):
    def bind(self, size=None, type=None, stride=0):
        """
            NormalBuffers dont need size.
        """
        if self.size and size is None:
            size = self.size
        if self.type and type is None:
            type = self.type
        if self.stride and stride is None:
            stride = self.stride
        super(NormalBuffer, self).bind(size, type, stride)
        glNormalPointer(type, stride, None)

    def state_bind(self, size=None,
                        type=None,
                        stride=0):
        """
            enables client state normals array
            and binds the buffer with pointer.
        """
        glEnableClientState(GL_NORMAL_ARRAY)
        self.bind(size, type, stride)

class TexCoordBuffer(VirtualBuffer):
    def bind(self, size=None, type=None, stride=0):
        """
            All args are needed
        """
        if self.size and size is None:
            size = self.size
        if self.type and type is None:
            type = self.type
        if self.stride and stride is None:
            stride = self.stride
        super(TexCoordBuffer, self).bind(size, type, stride)
        glTexCoordPointer(size, type, stride, None)

    def state_bind(self, size=None,
                        type=None,
                        stride=0):
        """
            enables client state texture coord array
            and binds the buffer with pointer.
        """
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        self.bind(size, type, stride)

class VertexBuffer(VirtualBuffer):
    def bind(self, size=None, type=None, stride=0):
        """
            All args are needed.
        """
        if self.size and size is None:
            size = self.size
        if self.type and type is None:
            type = self.type
        if self.stride and stride is None:
            stride = self.stride
        super(VertexBuffer, self).bind(size, type, stride)
        glVertexPointer(size, type, stride, None)

    def state_bind(self, size=None,
                        type=None,
                        stride=0):
        """
            enables client state vertex array
            and binds the buffer with pointer.
        """
        glEnableClientState(GL_VERTEX_ARRAY)
        self.bind(size, type, stride)

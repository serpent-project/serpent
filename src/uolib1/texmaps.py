# -*- coding: utf-8 -*-

from struct import unpack, pack
from common import NOT_SET, rgb_rgb555, rgb555_rgb, StandardSurface
from indexer import IndexCache

def image_from_tex_udata( udata = None ):
    if udata:
        size = 0
        if len(udata) == 0x4000: # 0x8000 bytes! 
            size = 128
        elif len(udata) == 0x1000:
            size = 64
        if not size:
            raise Exception( "Unknown Size!" + str(len(udata)))
        image = StandardSurface()
        image.new((size, size))
        for y in xrange(size):
            for x in xrange(size):
                image.dot( (x, y), rgb555_rgb(udata[ y * size + x ]) )
        return image

def tex_udata_from_image( image = None ):
    if image:
        size, sy = image.get_size()
        udata = []
        for y in xrange(size):
            for x in xrange(size):
                udata += [ rgb_rgb555(image.spot(x,y)) ]
        return udata

class TexIdxCache( IndexCache ):
    """ 
        Index Handler for Texmaps.idx Files based on IndexCache
    """
    standard_size = 0x8000

class TexmapsHandler( object ):
    filename = None
    def __init__(self, filename = None):
        self.filename = filename
        if self.filename:
            self.load(self.filename)
    def load(self, filename):
        pass
    def save(self, filename):
        pass
    def new(self):
        pass
    def get_texture(self, start = None, length = None):
        pass
    def set_texture(self, start = None, image = None):
        pass

class TexmapsFile( TexmapsHandler ):
    handle = None
    def load(self, filename):
        if filename:
            self.handle = open( filename, 'rb' )
    def get_texture(self, start = None, length = None):
        self.handle.seek( start )
        data = self.handle.read( length )
        udata = unpack( "<" + (len(data)/2) * "H", data  )
        return image_from_tex_udata(udata)

class TexmapsCache( TexmapsHandler ):
    udata = None
    def load(self, filename):
        if filename:
            f = open(filename, 'rb')
            data = f.read()
            f.close()
            self.udata = unpack( "<" + (len(data) / 2) * "H", data)
    def get_texture(self, start = None, length = None):
        if self.udata:
            return image_from_tex_udata( self.udata[ (start / 2) : (start + length) / 2 ] )

class Texmaps( object ):
    idx = None
    mul = None
    def __init__(self, idxname = None, mulname = None):
        if idxname and mulname:
            self.load(idxname, mulname)
    
    def load(self, idxname = None, mulname = None):
        self.idx = TexIdxCache( idxname )
        self.mul = TexmapsCache( mulname )
    
    def save(self, idxname = None, mulname = None):
        pass
    
    def get_entry(self, index):
        if index < len(self.idx):
            start, length, unknown = self.idx[ index ]
            if length:
                return self.mul.get_texture(start, length)
    
    def set_entry( self, index, image ):
        
        start, length, unknown = self.idx[ index ]
        size = length - start
        x, y = image.get_size()
        if (x == y) and (( x == 128 ) or (x == 64)):
            udata = tex_udata_from_image(image)
            #data = pack( "<" + "H" * len(udata), *udata )
            # first check if there is an image present with same size, so we simply replace it.
            if (x * y == size):
                self.udata[ start : start + length ] = udata
            # if not, we have to add it at the end.
            # @TODO
    
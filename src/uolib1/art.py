# -*- coding: utf-8 -*-

from struct import unpack, pack
from common import NOT_SET, rgb_rgb555, rgb555_rgb, StandardSurface
from indexer import IndexCache

def get_image_from_rawtile_udata(udata, surface = None):
    """generates a map image from unpacked data"""
    image = surface
    # print len(udata)
    if not surface:
        image = StandardSurface()
        image.new((44, 44))
    o = 0
    for y in xrange(22):
        p = y + 1
        pixels = udata[ o : o + p * 2 ]
        # spiegels = whole_data[ len(whole_data) / 2 + o: o + p * 2 - 1 ]            
        for x in xrange(len(pixels)):
            image.dot( (21 - y + x, y), rgb555_rgb( pixels[x] ) )
        o += len(pixels)
    for y in xrange(22):
        realy = 22 + y
        numx = 44 - y * 2
        pixels = udata[ o: o + numx ]
        for x in xrange(len(pixels)):
            image.dot( (x + y, realy), rgb555_rgb(pixels[x])  )
        o += len(pixels)
    return image

def get_image_from_runtile_udata(udata, surface = None):
    """generates image object from unpacked data."""
    if udata:
        # prepare header data
        width = udata[0]
        height = udata[1]
        if (width>=1024) or (width<=0) or (height<=0) or (height>=1024):
            return None
        if surface:
            image = surface
        else:
            image = StandardSurface()
            image.new(( width, height ))
        lstart = udata[2:2+height]
        udata = udata[2+height:]
        x = 0
        y = 0
        o = y
        while y < height:
            xoffset = udata[lstart[y] + o]
            xrun = udata[lstart[y]+ o + 1]
            # print "xrun %s xoffset %s" % (xrun, xoffset)
            o += 2
            if (xoffset + xrun) >= 2048:
                pass
            elif (xoffset + xrun) != 0:
                x += xoffset
                for i in xrange(xrun):
                    if (x+i) < width:
                        try:
                            image.dot( (x + i, y), rgb555_rgb(udata[ lstart[y] + o + i ] ) )
                        except:
                            print "Ooops"
                x += xrun
                o += xrun
            else:
                x = 0
                y += 1
                o = 0
        return image

def get_runtile_udata_from_image(image, correct_data = True):
    """
        creates unpacked data from an image for a runtile (items in art.mul)
        if correct_data is given, it will prepend [ 1, 0 ] as FLAG to the data.
    """
    udata = []
    udata += [ image.width ]
    udata += [ image.height ]
    offsets = []
    last_offset = 0
    offset_counter = 0
    image_data = []
    for y in xrange(image.height):
        actual_data = []
        offset_counter = 0
        for x in xrange(image.width):
            # TODO: this only works for pngs right now, since bmps have no alpha channel.
            r,g,b,a = image.spot( (x, y) )
            if a > 0:
                # visible, since alpha > 0
                actual_data += [ rgb_rgb555( (r, g, b) ) ] 
            else:
                # invisible, since alpha = 0
                if len(actual_data):
                    image_data += [ offset_counter, len(actual_data) ] + actual_data
                    actual_data = []
                    offset_counter = 0
                offset_counter += 1
        if len(actual_data):
            image_data += [ offset_counter, len(actual_data) ] + actual_data
            actual_data = []
        image_data += [0, 0]
        actual_data = []
        offsets += [ last_offset ]
        last_offset = len( image_data )
    udata += offsets + image_data
    if correct_data:
        udata = [ 1, 0 ] + udata
    return udata

def get_rawtile_udata_from_image(image, correct_data = True):
    """
        gets the unpacked data for a maptile from an image.
        if correct_data is given, data is corrected by sizing it to 1024 entries.
    """
    udata = []
    for y in xrange(22):
        p = y + 1
        for x in range( 22 - p, 22 + p ):
            # FIXME: alpha unneeded. maptiles dont know transparency anyway.
            r,g,b,a = image.spot( (x, y) )
            color = rgb_rgb555( (r, g, b) )
            udata += [ color ]
    for y in xrange(22):
        realy = 22 + y
        p = 22 - y
        for x in range( 22 - p, 22 + p ):
            r,g,b,a = image.spot( (x, realy) )
            color = rgb_rgb555( (r, g, b) )
            udata += [ color ]
    if correct_data:
        udata += [ 0 for j in xrange(12) ]
    return udata

class ArtIdxCache( IndexCache ):
    """ 
        Index Handler for ArtIdx Files based on IndexCache
    """
    standard_size = 0x8000
    
class ArtHandler( object ):
    def __init__(self, file_name = None):
        if file_name:
            self.load(file_name)
    def load(self, file_name = None):
        self.file_name = file_name
    def save(self, file_name = None) : pass
    def new(self): pass
    def get_tile_static(self, pos, length):
        """use this function to retrieve a static tile as image.""" 
        pass
    def get_tile_map(self, pos, length):
        """use this function to retrieve a map tile as image""" 
        pass
    def set_tile_static(self, pos, pic):
        """use this function to set an image..."""
    def set_tile_map(self, pos, pic):
        """use this function to set an image..."""
    
    # --- builtin functions ---
    def runtile_data(self, udata, surface = None):
        """
        generates image object from unpacked data.
        @deprecated: use get_image_from_runtile_udata directly.
        """
        return get_image_from_runtile_udata(udata, surface)
        
    def rawtile_data(self, udata, surface = None):
        """
        generates a map image from unpacked data
        @deprecated: use get_image_from_rawtile_udata directly.
        """
        return get_image_from_rawtile_udata(udata, surface)
    
class ArtFile( ArtHandler ):
    handle = None
    def load(self, file_name = None):
        self.file_name = file_name
        if self.handle:
            self.handle.close()
        self.handle = open(file_name, 'rb')
    
    def rawtile_data_rot(self, udata):
        """Alazane's Method of rotating the Maptile to a 44x44 bitmap
        a bit buggy d'oh."""
        image = StandardSurface()
        image.new((44, 44))
        xstart = 0
        ystart = 1
        i = 0
        while xstart <= 44:
            x = xstart
            y = ystart
            while (x  <= 44) and (y >= 0):
                image.dot ( (x, y), rgb555_rgb( udata[i] ) )
                image.dot ( (x+1, y), rgb555_rgb( udata[i] ) )
                image.dot ( (x, y+1), rgb555_rgb( udata[i] ) )
                i += 1
                x += 1
                y -= 1
            if ystart < 43:
                ystart += 2
            elif ystart == 43:
                ystart += 1
                xstart += 1
            else:
                xstart += 2
        return image          
    
    def get_tile_static(self, pos, length):
        if self.handle and pos != NOT_SET and (length != NOT_SET or length != 0):
            # read the data:
            self.handle.seek(pos)
            data = self.handle.read( length )
            whole_data = unpack( "<" + "H" * (len(data) / 2), data )
            try:
                return self.runtile_data(whole_data[2:])
            except:
                return None
    
    def get_tile_map(self, pos, length):
        if self.handle and pos != NOT_SET and (length != NOT_SET or length != 0):
            # read the data:
            self.handle.seek(pos)
            data = self.handle.read( length )
            whole_data = unpack( "<" + "H" * (len(data) / 2), data )
            try:
                return self.rawtile_data(whole_data)
            except:
                return None
    
class ArtWriter( object ):
    """
        does not use a cache, writes directly to file.
        you should still call flush at the end to be sure
        also to be compatible with cache-writers.
    """
    def __init__(self, file_name = None):
        self.file_name = file_name
        self.handle = None
        if file_name:
            self.create()
            
    def create(self):    
        self.handle = open(self.file_name, 'wb')
    
    def flush(self):
        self.handle.flush()
    
    def append_udata(self, udata):
        """appends unpacked data to the file
        it is directly converted.
        """
        # pack the data
        data = pack( "<" + "H" * len(udata), *udata )
        # send it to append
        return self.append(data)
        
    def append(self, data):
        if data and self.handle:
            pos = self.handle.tell()
            self.handle.write( data )
            return ( pos, len(data) )
        return (None, None)

class ArtWriterUdataCache( ArtWriter ):
    """
        for linear writing of a new art file.
        writes in cache first. call flush at end to write file.
        use append_udata mainly, since append is not usable here.
    """
    def __init__(self, file_name = None):
        self.file_name = file_name
        self.buffer = []
        self.length = 0
    
    def create(self):
        self.buffer = []
        self.length = 0
        
    def flush(self):
        if self.file_name:
            # create stringbuffer by packing buffer
            pbuffer = pack( "<" + "H" * len(self.buffer), *self.buffer )
            handle = open(self.file_name, 'wb')
            handle.write(pbuffer)
            handle.close()
    
    def append_udata(self, udata):
        if udata:
            datalength = len(udata) * 2
            self.buffer += udata
            self.length += datalength
            return (self.length - datalength, datalength)
        return (None, None)
    
class ArtCache(ArtFile):
    buffer = None
    def load(self, file_name = None):
        self.file_name = file_name
        f = open(file_name, 'rb')
        self.buffer =  f.read()
        f.close()
    
    def get_tile_static(self, pos, length):
        if self.buffer and pos != NOT_SET and (length != NOT_SET or length != 0):
            # read the data:
            data = self.buffer[ pos: pos + length ]
            whole_data = unpack( "<" + "H" * (len(data) / 2), data )
            try:
                return self.runtile_data(whole_data[2:])
            except Exception, e:
                return None
    
    def get_tile_map(self, pos, length):
        if self.buffer and pos != NOT_SET and (length != NOT_SET or length != 0):
            # read the data:
            data = self.buffer[ pos: pos + length ]
            whole_data = unpack( "<" + "H" * (len(data) / 2), data )
            try:
                return self.rawtile_data(whole_data)
            except:
                return None

class ArtCacheUnpacked( ArtFile ):
    cache = None
    def load(self, file_name = None):
        self.file_name = file_name
        f = open(file_name, 'rb')
        buffer =  f.read()
        f.close()
        self.cache_from_buffer(buffer)
    
    def cache_from_buffer(self, buffer):
        self.cache = unpack( "<" + "H" * (len(buffer) / 2), buffer ) 
    
    def get_tile_static(self, pos, length):
        if self.cache and pos != NOT_SET and (length != NOT_SET or length != 0):
            # read the data:
            data = self.cache[ pos / 2 + 2: (pos / 2) + (length / 2) ]
            try:
                return self.runtile_data(data)
            except:
                return None
    
    def get_tile_map(self, pos, length):
        if self.cache and pos != NOT_SET and length != NOT_SET and length != 0:
            # read the data:
            data = self.cache[ pos / 2: pos / 2 + length / 2 ]
            try:
                return self.rawtile_data(data)
            except:
                return None
        else:
            return None

class Art( object ):
    """
    For using Art. 
    It uses a Cache which decodes slower, but needs less memory and startup time.
    You may use load_all() to load everything in an unpacked cache, which should be
    the fastest way to read data.
    """
    def __init__(self, artidx_file, artmul_file):
        self.load(artidx_file, artmul_file)
    
    def load_all(self):
        if isinstance(self.artmul, ArtCacheUnpacked):
            return False
        elif isinstance(self.artmul, ArtCache):
            new_artmul = ArtCacheUnpacked()
            new_artmul.cache_from_buffer(self.artmul.buffer)
            self.artmul = new_artmul
            return True
        elif isinstance(self.artmul, ArtFile):
            new_artmul = ArtCacheUnpacked( self.artmul.file_name )
            self.artmul = new_artmul
            return True
        return False
    
    def load_idx(self, file_name, ArtIdxType = ArtIdxCache):
        self.artidx = ArtIdxType(file_name)
    
    def load_art(self, file_name, ArtType = ArtCache):
        self.artmul = ArtType( file_name )
    
    def get_tile(self, number):
        if number < 0x4000:
            return self.get_tile_map( *self.get_position(number) )
        else:
            return self.get_tile_static( *self.get_position(number) )
    
    def get_tile_map(self, pos, length):
        return self.artmul.get_tile_map(pos, length)
    
    def get_tile_static(self, pos, length):
        return self.artmul.get_tile_static(pos, length)
    
    def get_position(self, number):
        return self.artidx.get_position(number)
    
    def set_tile_map(self, pos, pic):
        pass
    
    def set_tile_static(self, pos, pic):
        pass
    
    def save(self, artidx_name, artmul_name):
        """saves everything"""
        pass
    
    def load(self, artidx_name, artmul_name):
        """loads everything"""
        self.load_idx( artidx_name, ArtIdxCache )
        self.load_art( artmul_name, ArtCache )
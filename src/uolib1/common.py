import Image, ImageDraw

class MapRelated( object ):
    map_x = 768
    map_y = 512
    size = 0

NOT_SET = 0xffffffff

def rgb555_rgb(rgb):
    r = (rgb >> 10) & 0x1f
    g = (rgb >> 5) & 0x1f
    b = rgb & 0x1f
    m = 0xff / 0x1f
    return (r * m, g * m, b * m)

def rgb_rgb555(rgb555):
    r, g, b = rgb555
    m = 0xff / 0x1f
    return (r << 10) / m + (g << 5) / m + (b / m)
    

class Surface(object):
    """abstract class for Surfaces."""
    # following MUST be implemented ATM.
    def new(self, size): pass
    def dot(self, pos, color): 
        """ draws a pixel. """ 
        pass
    def spot(self, pos): 
        """ returns color information of a pixel """
        pass

class PILSurface( Surface ):
    """basic class to have imaging support
    wraps PIL basicly. however you can create your own."""
    def __init__(self, image = None):
        self.image = image
        self.image_data = None
        self.draw = None
    
    def new(self, size):
        self.width, self.height = size
        self.image = Image.new( 'RGBA', size )
    
    def load(self, file_name):
        self.image = Image.open( file_name )
        self.width, self.height = self.image.size
    
    def get_image(self):
        return self.image
    
    def get_size(self):
        return (self.width, self.height)
    
    def save(self, file_name, mode = 'PNG'):
        return self.image.save(file_name, mode)
    
    def dot(self, pos, color):
        """put a color on a coordinate"""
        if not self.draw:
            if not self.image:
                raise Exception("You have to load an image or create a new one first.")
            self.draw = ImageDraw.Draw(self.image)
        self.draw.point( pos, fill=color )
    
    def spot(self, pos):
        """get the color at a coordinate"""
        if not self.image:
            return None
        if not self.image_data:
            self.image_data = self.image.load()
        return self.image_data[ pos[0], pos[1] ]
    
StandardSurface = PILSurface
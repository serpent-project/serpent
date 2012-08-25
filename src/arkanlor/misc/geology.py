"""
    Taken from mudpie.
    However I have to align the classes a bit to allow offset rendering
    of the same noise. (g4b)
    
    http://code.google.com/p/mudpie/
    
    MIT License
    http://opensource.org/licenses/mit-license.php
    
    Copyright (c) 2010 Eric Fredricksen

    Permission is hereby granted, free of charge, to any person obtaining a 
    copy of this software and associated documentation files (the "Software"), 
    to deal in the Software without restriction, including without limitation 
    the rights to use, copy, modify, merge, publish, distribute, sublicense, 
    and/or sell copies of the Software, and to permit persons to whom the 
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in 
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY 
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT 
    OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
    THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
# TODO:
# hydrologic erosion
# eEdgeEffects = 'eeNone eeWrap eeFastWrap eeLimit eeFastBounce'.split()


import numpy, math, random

def Generate(shape, generator):
    """Generate terrain with position-independent generating function"""
    t = Terrain(shape)
    for y in range(t.height()):
    for x in range(t.width()):
        t.z[x, y] = generator()
    return t


def WhiteNoise(shape):
    """Generate terrain with white noise on [0,1)"""
    return Generate(shape, random.random)


def MidpointDisplacementNoise(shape, n=None, persistence=0.5):
    """Generate 1/f, aka pink, noise using midpoint displacement via the
    diamond-square algorithm"""

    terrain = Terrain(shape)

    def item(x, y):
    return terrain.z[x % terrain.width(), y % terrain.height()]

    def bishopsum(x, y, d):
    return (item(x - d, y - d) + item(x + d, y - d) +
            item(x - d, y + d) + item(x + d, y + d))

    def rooksum(x, y, d):
    return (item(x, y - d) +
            item(x - d, y) + item(x + d, y) +
                    item(x, y + d));

    W, H = terrain.z.shape
    if not n:
    # find largest power of 2 <= to smallest dimension - that will be
    # our starting fractal scale
    n = 1
    while n <= min(W, H) / 2:
        n += n

    sigma = 0.5

    # fill in initial values
    for y in range(0, W, n):
    for x in range(0, H, n):
        terrain.z[x, y] = random.gauss(0, sigma)

    # at each scale level, do your thing
    while n > 1:
    n /= 2
    sigma *= persistence
    for y in range(n, H, n + n):
        for x in range(n, W, n + n):
        terrain.z[x, y] = random.gauss(bishopsum(x, y, n) / 4.0,
                                        sigma * math.sqrt(2.0))

    for y in range(0, H, n + n):
        for x in range(n, W, n + n):
        terrain.z[x, y] = random.gauss(rooksum(x, y, n) / 4.0, sigma)

    for y in range(n, H, n + n):
        for x in range(0, W, n + n):
        terrain.z[x, y] = random.gauss(rooksum(x, y, n) / 4.0, sigma)

    return terrain


# Not sure what my original source was for this, but this is
# related, though different:
# http://www.gamedev.net/reference/articles/article900.asp
def SpectralSynthesis(shape, dimension=0.9, numwaves=100):
    """Generate terrain as a sum of random sin waves"""
    tera = Terrain(shape)
    W, H = tera.shape()

    MAXTAULOG2 = math.log(max(*tera.z.shape), 2)
    MINTAULOG2 = 1.0

    waves = []
    for i in range(numwaves):
    Tau = 2 ** random.uniform(MINTAULOG2, MAXTAULOG2)    # period
    Nu = 1 / Tau    # frequency
    Alpha = random.random() * math.pi    # orientation
    waves.append((
        Tau ** dimension, # amplitude
        random.random() * 2 * math.pi, # offset
        Nu * math.cos(Alpha), # freq_x
        Nu * math.sin(Alpha)))            # freq_y

    for j in range(H):
    for i in range(W):
        v = 0.0
        for amp, offset, nu_x, nu_y in waves:
        tera.z[i, j] += amp * math.sin(nu_x * i + nu_y * j + offset)

    return tera


def FaultNoise(shape, numFaults=200):
    tera = Terrain(shape)
    W, H = tera.z.shape

    formulae = []
    for x in range(numFaults):
    # Pick a random line though some (x0,y0) with slope m
    alpha = random.random() * 2 * math.pi    # angle of line
    m = math.tan(alpha)                    # slope
    x0, y0 = [random.randrange(x) for x in (W, H)]
    # y = mx + b
    b = y0 - m * x0;
    # displace one side of this line this much:
    d = random.random() - 0.5
    formulae.append((m, b, d))

    for y in range(H):
    for x in range(W):
        for m, b, d in formulae:
        if y > m * x + b:
            tera.z[x, y] += d

    return tera


def PerlinNoise(shape, Nrange=None, B=256):

    tera = Terrain(shape)

    def perlin_precomps(dimensions, B=256):
    "Build random permutation and gradient vectors"

    def permutation(n):
        result = range(n)
        for i in range(n):
        j = random.randrange(n)
        t = result[j]
        result[j] = result[i]
        result[i] = t
        return result

    def normalize_vector(v):
        s = math.sqrt(sum([a * a for a in v]))
        return [a / s for a in v]

    p = permutation(B)
    g = [normalize_vector([(random.random() * 2.0) - 1.0
                             for j in range(dimensions)])
         for i in range(B)]
    # avoid need for modulo op
    p += p + p[:2]
    g += g + g[:2]
    return p, g

    def perlin_noise2d(point, B, p, g):
    def setup(v):
        b0 = int(v % B)
        b1 = (b0 + 1) % B
        r0 = v % 1.0
        r1 = r0 - 1.0
        return b0, b1, r0, r1
    ((bx0, bx1, rx0, rx1), (by0, by1, ry0, ry1)) = [setup(coord) for coord in point]

    i = p[bx0]
    j = p[bx1]

    b00 = p[i + by0]; b10 = p[j + by0]
    b01 = p[i + by1]; b11 = p[j + by1]

    sx = s_curve(rx0)
    sy = s_curve(ry0)

    u = numpy.dot([rx0, ry0], g[b00])
    v = numpy.dot([rx1, ry0], g[b10])
    a = u + sx * (v - u)    # linear interpolation in x

    u = numpy.dot([rx0, ry1], g[b01])
    v = numpy.dot([rx1, ry1], g[b11])
    b = u + sx * (v - u)    # linear interpolation in x

    return a + sy * (b - a)    # linear interpolation in y


    p, g = perlin_precomps(2, B)

    for n in Nrange or range(1, 6 + 1):
    R = 2.0 ** n    # could speed up the 0 case by losing interpolation!
    for j in range(tera.height()):
        for i in range(tera.width()):
        # put abs() around here for fire effect
        tera.z[i, j] += R * perlin_noise2d((i / R, j / R), B, p, g)

    return tera


def Grid(shape):
    tera = Terrain(shape)

    def leastbit(n):
    "Return position of the least significant 1 bit (or 1)"
    if not n: return 1
    m = 1
    v = 0.0
    while not (m & n):
        m += m
        v += 1
    return v

    tera.z = numpy.array(
    [[max([leastbit(c) for c in (x, y)])
        for y in range(tera.height())]
     for x in range(tera.width())])

    return tera


def Voronoi(shape, coefficients=(-1, 1), points=10):

    tera = Terrain(shape)

    def d(dx, dy):
    dx = abs(dx)
    dy = abs(dy)
    if (dx > 0.5): dx = 1.0 - dx
    if (dy > 0.5): dy = 1.0 - dy
    #return dx**2 + dy**2 # faster but this isn't the major time sink
    return math.sqrt(dx ** 2 + dy ** 2)

    if type(points) == type(1):
    # Points is a count of points rather than the actual points
    points = map(lambda x: (random.random(), random.random()),
                 range(points))
    elif not points:
    # Infer number of points from number of coefficients
    points = map(lambda x: (random.random(), random.random()),
                 coefficients)
    W, H = tera.shape()
    for y in range(H):
    fy = 1.0 * y / H
    for x in range(W):
        fx = 1.0 * x / W
        ranges = map(lambda p: d(p[0] - fx, p[1] - fy), points)
        ranges.sort()
        tera.z[x, y] = numpy.dot(coefficients, ranges[:len(coefficients)])

    return tera


class Terrain:

    def __init__(self, shape=None, data=None,
                 sealevel=None, palette=None):
    if data != None:
        self.z = data + 0
    else:
        if shape:
        if type(shape) == type(0):
            shape = (shape, shape)
        else:
        shape = (64, 64)
        self.z = numpy.zeros(shape)
    self.sealevel = sealevel or 0.5
    self.palette = palette

    def shape(self):
    return self.z.shape

    def width(self):
    return self.z.shape[0]

    def height(self):
    return self.z.shape[1]

    def copy(self):
    return Terrain(data=self.z, sealevel=self.sealevel, palette=self.palette)

    def reset(self):
    self.z = numpy.zeros(self.z.shape)
    return self

    def scaleup(self):
    """Double the terrain resolution with nearest neighbor"""
    a = self.z
    self.z = a.repeat(tuple(2 * numpy.ones(a.shape[0])), 0)
    self.z = self.z.repeat(tuple(2 * numpy.ones(self.height())), 1)
    return self

    def tile(self):
    self.z = numpy.concatenate((self.z, self.z))
    self.z = numpy.concatenate((self.z, self.z), 1)
    return self

    def image(self, palette=None):
    return image(self.z, palette or self.palette or None)

    def display(self, palette=None):
    display(self.z, palette or self.palette or None)

    def render3D(self, palette=None):
    render3D(self.z, palette or self.palette or None)


    def normalize(self):
    if self.z.max() > self.z.min():
        self.z = (self.z - self.z.min()) / (self.z.max() - self.z.min())
    else:
        self.reset()
    return self



    def distort(self, blocksize=16, deviation=4):
    """Laterally distort height field (move the height field around on the horizonal plane, that is)"""

    def interpolate(p):
        p0 = [int(p[i]) % self.z.shape[i] for i in range(2)]
        p1 = [(p0[i] + 1) % self.z.shape[i] for i in range(2)]
        f = [s_curve(pi % 1.0) for pi in p]
        x0 = self.z[p0[0], p0[1]] * (1.0 - f[0]) + self.z[p1[0], p0[1]] * f[0]
        x1 = self.z[p0[0], p1[1]] * (1.0 - f[0]) + self.z[p1[0], p1[1]] * f[0]
        return x0 * (1.0 - f[1]) + x1 * f[1]

    W, H = self.shape()
    g = numpy.array([[[random.gauss(0, deviation)
                         # (random.random()-0.5)*2.0*deviation
                         for j in range(2)]
                        for j in range(H / blocksize)]
                     for i in range(W / blocksize)])
    zr = self.z + 0.0
    for y in range(H):
        y0 = y / blocksize
        y1 = (y0 + 1) % (H / blocksize)
        fy = s_curve(float(y) / blocksize - y0)
        for x in range(W):
        x0 = x / blocksize
        x1 = (x0 + 1) % (W / blocksize)
        fx = s_curve(float(x) / blocksize - x0)
        gy0 = g[x0, y0] * (1.0 - fx) + g[x1, y0] * fx
        gy1 = g[x0, y1] * (1.0 - fx) + g[x1, y1] * fx
        gt = gy0 * (1.0 - fy) + gy1 * fy
        zr[x, y] = interpolate([x, y] + gt)
    self.z = zr
    return self


    def distort_fractally(self, degree=0.125, max_blocksize=5):
    """Apply lateral distorion on a range of orders of magnitude"""
    for r in [2 ** i for i in range(1, max_blocksize + 1)]:
        self.distort(r, r * degree)
    return self


    def smooth(self):
    """Smooth on the Moore neighborhood; apply this filter:
    1 2 1
    2 4 2
    1 2 1
    """
    n = north(self.z)
    s = south(self.z)
    self.z = (self.z * 4 + (n + s + east(self.z) + west(self.z)) * 2 +
                (west(n) + east(n) + west(s) + east(s))) / 16
    return self


    def smooth4(self):
    """Smooth on the Von Neumann neighborhood; apply this filter:
    0 1 0
    1 2 1
    0 1 0
    This appears to be very close to twice as fast and half as smoothing
    as the Moore neighborhood version, with the same final quality"""
    self.z = self.z / 3 + (north(self.z) + south(self.z) +
                             east(self.z) + west(self.z)) / 6
    return self


    # Leaves sculpted & hills which is nice. Very smoothing when
    # fill=True. Can look cratery when fill=False. Somewhere between mean
    # and mean+std of (z-north(z)).clip(0,infinity) is a good choice for
    # talus. Has some axis-oriented effects when cranked up too high.
    def thermally_erode(self, talus=0.01, erosion=0.5, fill=False):
    """Apply thermal erosion wherein steeper slopes crumble"""
    nsew = [(self.z - x(self.z)).clip(fill and -999.0 or 0.0, 999.0)
            for x in north, south, east, west]
    nsew = [(x - x.clip(-talus, talus)) for x in nsew]
    self.z = self.z - sum(nsew) * (erosion / 4.0)
    return self


    def slope_map(self):
    """Maximum difference from Von Neumann neighbors at each point"""
    return numpy.maximum(numpy.maximum(abs(self.z - north(self.z)),
                                         abs(self.z - south(self.z))),
                         numpy.maximum(abs(self.z - east(self.z)),
                                         abs(self.z - west(self.z))))


    def erosion_score(self):
    """Actually a playability score, from
    "Realtime Procedural Terrain Generation"
    Realtime Synthesis of Eroded Fractal Terrain for Use in Computer Games
    by Jacob Olsen
    http://oddlabs.com/download/terrain_generation.pdf
    The score favors maps with lots of flat areas but lots of variation.
    """
    m = self.slope_map()
    return m.std() / m.mean()


    def meadowize(self):
    """Fill in local minima so that the entire above-sea-level portion of
    the map flows downhill to the sea. Not sure if this is worth anything."""
    W, H = self.z.shape
    def vnn(x, y):
        VNN = (-1, 0), (1, 0), (0, -1), (0, 1)    # Von Neumann neighborhood vectors
        return [((x + dx) % W, (y + dy) % H) for dx, dy in VNN]
    blessing = numpy.ones(self.z.shape) * self.z.max() + 1.0
    blessed = [(x, y) for y in range(H) for x in range(W)
                 if self.z[x, y] <= self.sealevel]
    for x, y in blessed:
        blessing[x, y] = self.z[x, y] # self.sealevel
    todo = set()
    for x, y in blessed:
        for x1, y1 in vnn(x, y):
        if blessing[x1, y1] > self.sealevel:
            todo.add((x1, y1))
    while todo:
        x, y = todo.pop()
        b = max(self.z[x, y], min([blessing[xn, yn] for xn, yn in vnn(x, y)]))
        if b < blessing[x, y]:
        blessing[x, y] = b
        todo |= set([(x1, y1) for (x1, y1) in vnn(x, y)
                     if max(b, self.z[x1, y1]) < blessing[x1, y1]])
    self.z = blessing
    return self

    def hydraulically_erode(self, sealevel= -1.0, rainfall=0.01, solubility=0):
    FLAT = 0.01
    W, H = self.z.shape
    def vnn(x, y):
        VNN = (-1, 0), (1, 0), (0, -1), (0, 1)    # Von Neumann neighborhood vectors
        return [((x + dx) % W, (y + dy) % H) for dx, dy in VNN]
    water = numpy.ones(self.z.shape) * rainfall
    # todo: more rain at higher altitudes?
    # todo: more rain on certain slopes?
    points = [(self.z[x, y], (x, y)) for y in range(H) for x in range(W)]
    points.sort(reverse=True)
    for h, (x, y) in points:
        if h <= sealevel:
        water[nx, ny] = 0.0
        continue
        lownabes = [(FLAT + h - self.z[xn, yn], (xn, yn)) for (xn, yn) in vnn(x, y)
                    if self.z[xn, yn] <= h]
        loss = sum([dh for (dh, c) in lownabes])
        for nh, (nx, ny) in lownabes:
        water[nx, ny] += water[x, y] * nh / loss
    #return water
    return self


    # I don't know which, if any, of these hydralic erosion algorithms are
    # worth a shit. Here's to great documentation.

    def hydrode(self, iters, rainfall=0.02, solubility=0.1, evap=0.3):

    def drip(rain, speed=0.5):
        tz = self.z + rain
        NSEW = north, south, east, west
        drop = numpy.array([(tz - x(tz)).clip(0.0, 999.0)
                            for x in NSEW])
        flowing = numpy.minimum(drop.max(0), rain) * speed
        flowto = drop.argmax(0)
        nada = numpy.zeros(self.z.shape)
        result = 0 - flowing
        for i in range(4):
        dflow = numpy.where(flowto - i, nada, flowing)
        result += (south, north, west, east)[i](dflow)
        return result

    z = self.z + 0
    rain = z * 0
    #rain = z * 0 + rainfall
    for i in range(iters):
        # rainfall (which dissolves when is falls)
        rain += rainfall
        #z -= rainfall * solubility
        # flow
        d = drip(z, rain)
        z += d * solubility
        rain += d
        # evaporate
        #z += evap * solubility * rain
        #rain -= evap * rain
    # final evap
    #z += rain * solubility
    self.z = z
    return self


def image(z, palette=None):
    from PIL import Image
    w, h = z.shape[:2]
    i = Image.new(palette and "P" or "L", z.shape, None)
    if palette: i.putpalette(palette)
    for y in range(h):
    for x in range(w):
        i.putpixel((x, y), 256 * z[x, y])
    return i


def display(z, palette=None):
    image(z, palette).show()


def render3D(terrain, palette=None):
    from PIL import Image
    w, h = terrain.shape[:2]
    im = Image.new("P" if palette else "L", terrain.shape)
    if palette: im.putpalette(palette)
    import ImageDraw
    draw = ImageDraw.Draw(im)
    y0 = 1.0 * h
    for y in range(h):
    yscale = y0 / (y0 + (h - y))
    j0bar = yscale
    j0 = (h / 2) * (1 + j0bar)
    #print y, yscale, j0bar, h, j0
    for x in range(w):
        z = terrain[x, y]
        zbar = 1 - z
        jbar = yscale * zbar
        j = (h / 2) * (1 + jbar)
        xbar = w / 2 - x
        ibar = xbar * yscale
        i = h / 2 - ibar
        c = 256 * z
        if y == w - 1: c = 0
        if (0 <= i) and (i < w) and (0 <= j) and (j < h):
        draw.line((i, j, i, j0), c)
    im.show()


def s_curve(t):
    return t * t * (3.0 - 2.0 * t)


def north(matrix):
    return numpy.concatenate((matrix[1:, :], matrix[:1, :]))

def east(matrix):
    return numpy.concatenate((matrix[:, -1:], matrix[:, :-1]), 1)

def south(matrix):
    return numpy.concatenate((matrix[-1:, :], matrix[:-1, :]))

def west(matrix):
    return numpy.concatenate((matrix[:, 1:], matrix[:, :1]), 1)


def geographic_palette():
    result = []
    for i in range(80):
    result += [92, 92, i + 128]
    for i in range(80, 128):
    result += [64, i, 64]
    for i in range(128, 192):
    result += [i, i, 0]
    for i in range(192, 256):
    v = 128 + i / 2
    result += [v, v, v]
    return result

def land_sea_palette(sealevel=0.5):
    if type(sealevel) == type(1.0):
    sealevel = int(sealevel * 256)
    c2 = sealevel / 2
    t = 256 - sealevel
    result = []
    for i in range(c2):
    result += [0, 0, 255 * i / c2]
    for i in range(c2, sealevel):
    result += [0, 255 * (i - c2) / c2, 255]
    for i in range(t):
    result += [i * 255 / t, 128 + i * 128 / t, 0]
    return result

def thermal_palette():
    """Shows much contrast between values"""
    result = []
    for i in range(64):
    result += [0, 0, i * 4]
    for i in range(64, 128):
    result += [0, (i - 64) * 4, 0]
    for i in range(128, 192):
    result += [(i - 128) * 4, 0, 0]
    for i in range(192, 256):
    result += [(i - 192) * 4, (i - 192) * 4, 0]
    return result

def fire_palette():
    result = []
    for i in range(128):
    result += [i + 64, 0, 0]
    for i in range(128, 256):
    result += [i / 2 + 128, (i - 128) * 3 / 2, 0]
    return result

def zebra_palette():
    result = []
    for i in range(256):
    x = math.sin(i / 16.0)
    x = math.floor((1.0 - (x ** 2)) * i)
    result += [x, i, x]
    return result

# Unused, evidently
#def nonlinear_choice(perm, *indices):
#    v = 0
#    for i in indices:
#    v = perm[(i + v) % len(perm)]
#    return v



"""

Water erosion; not yet ported from Pascal. There's other h2o erosion
above. Is this different?

def applyfilter( array2D<T> & z, const array2D<T> & f )
begin
    // applies f as a filter on z, its advisable to
    // have f have odd dimensions, or it'll be cockeyed

    array2D<T> z2(z);

    const int xsize = z.Width();
    const int ysize = z.Height();

    const int xoff = f.Width() / 2;
    const int yoff = f.Height() / 2;

    int i, j, fi, fj;
    T ftotal = 0;

         for( fj = 0; fj < f.Height(); fj++ )
            for( fi = 0; fi < f.Width(); fi++ )
                ftotal += f(fi,fj);

        if(ftotal = 0)
        begin
            Application->MessageBox( "Filter sums to zero","OberMapper",MB_OK);
            return;
        end;

        for( j = 0; j < ysize; j++ )
        begin
            for( i = 0; i < xsize; i++ )
                begin
                    T total = 0;

                for( fj = 0; fj < f.Height(); fj++ )
                    for( fi = 0; fi < f.Width(); fi++ )
                        total += z2(i+fi-xoff,j+fj-yoff) * f(fi,fj);

            // truncates ints, but so what.
                z(i,j) = total / ftotal;
        end;
    end;
end;


def TFormOber::rain()
begin
    for( int i = 0; i < fRain.Height() * fRain.Width(); ++i )
        fRain[i] += 100;
end;

//---------------------------------------------------------------------------

def TFormOber::normrain()
begin
    minimax<int> x;
    for( int i = 0; i < fTerrain.Height() * fTerrain.Width(); ++i )
        if( fTerrain[i] > 0 )
        begin
            //if( fRain[i] > 0 ) fRain[i] = 10000 - 10000 / fRain[i];
            x = fRain[i];
        end;
        else
        begin
            fRain[i] = 0;
        end;

    if( x.Spread() > 0 )
        for( int i = 0; i < fTerrain.Height() * fTerrain.Width(); ++i )
            if( fTerrain[i] > 0 )
                fRain[i] = (10000 * (fRain[i]- x.Min())) / x.Spread();
//                fRain[i] = fRain[i] > x.Mean() ? 10000 : 0;
end;

//---------------------------------------------------------------------------

int TFormOber::alt(int i, int j)
begin
    return fTerrain(i,j) + fRain(i,j);
end;


//---------------------------------------------------------------------------

def TFormOber::trickle()
begin
    array2D<int> rerun(fRain);
    array2D<int> reter(fTerrain);

    for( int j = 0; j < fRain.Height(); ++j )
        for( int i = 0; i < fRain.Width(); ++i )
        begin
            if( fTerrain(i,j) > 0 )
            begin
                int lowi = i;
                int lowj = j;

#define alt(i,j) fTerrain(i,j) + fRain(i,j)
                if( alt(i-1,j) < alt(lowi,lowj) ) begin lowi=i-1; lowj=j; end;
                if( alt(i+1,j) < alt(lowi,lowj) ) begin lowi=i+1; lowj=j; end;
                if( alt(i,j-1) < alt(lowi,lowj) ) begin lowi=i; lowj=j-1; end;
                if( alt(i,j+1) < alt(lowi,lowj) ) begin lowi=i; lowj=j+1; end;
                const int diff = fTerrain(i,j) - fTerrain(lowi,lowj);

                int xfer = (alt(i,j)-alt(lowi,lowj)) / 2;
                if( xfer > fRain(i,j) ) xfer = fRain(i,j);
                rerun(i,j) -= xfer;
                rerun(lowi,lowj) += xfer;
                if( diff > 0 )
                begin
                    const int tfer = xfer / 2;//(diff + 3) / 4;
                    //reter(lowi,lowj) += tfer / 2;
                    reter(i,j) -= tfer;
                end;
            end;
        end;

    fTerrain = reter;
    fRain = rerun;
end;

def __fastcall TFormOber::RainstogramClick(TObject *Sender)
begin
    FormHisto->Render( fRain );
    FormHisto->Show();
end;

#define MAXI 10000

begin
    start();
    for( int i = 0; i < fTerrain.Height() * fTerrain.Width(); ++i )
        fTerrain[i] = -fTerrain[i];
    done();
end;
//---------------------------------------------------------------------------



//---------------------------------------------------------------------------
def __fastcall TFormTools::RainClick(TObject *Sender)
begin
    start();

    fRain = 0;

    for( int i = 0; i < UpDown1->Position; ++i )
    begin
        FormOber->rain();
        FormOber->trickle();
    end;

 //    normrain();

    done();
end;

//---------------------------------------------------------------------------

//---------------------------------------------------------------------------



//---------------------------------------------------------------------------
def __fastcall TFormTools::MakeWavesClick(TObject *Sender)
begin
    start();
    fBm( fTerrain, atof(fbmDim->Text.c_str()), StrToInt(fbmWaves->Text) );
    //normalize( fTerrain, -MAXI, MAXI );
    done();
end;
//---------------------------------------------------------------------------

//---------------------------------------------------------------------------

def TFormHisto::Render( array2D<int> & terra )
begin
    dib.Fill( 0x404040 );

    const int s = 400;
    int his[s];
    assert( s = PaintBox1->Width );
    memset( his, 0, sizeof(his) );

    for( int i = 0; i < terra.Width() * terra.Height(); ++i )
    begin
        int off = ((terra[i] + 10000) * s) / 20000;
        if( off < 0 ) off = 0;
        if( off >= s ) off = s;
        his[off]++;
    end;

    minimax<int> m;
    for( int i = 0; i < s; ++i )
        m = his[i];

    for( int i = 0; i < s; ++i )
    begin
        int Colorize( int h, int r );
        const int co = Colorize( ((i - (s/2)) * 20000) / s, 0 );
        for( int j = PaintBox1->Height-(1+(his[i] * PaintBox1->Height) / (m.Max()));
             j < PaintBox1->Height; ++j )
        begin
            if( j < 0 ) j = 0;    //$weak
            dib.Pixel(i,j) = co;
        end;
    end;

    PaintBox1->Invalidate();
end;

"""

class Vector(object):
    __slots__ = ('data', 'max_length')
    max_length = None # this vector has no boundaries.
    def __init__(self, *args):
        self.data = args
    def __repr__(self):
        return repr(self.data)
    def __add__(self, other):
        """ adds two vectors, does not check for size. """
        ret = []
        for j in range(len(self.get_data())):
            if isinstance(other, int) or isinstance(other, float):
                ret.append(self.data[j] + other)
            else:
                ret.append(self.data[j] + other.data[j])
        return self.__class__(*ret)
    def __div__(self, other):
        """ divides two vectors """
        ret = []
        for j in range(len(self.get_data())):
            if isinstance(other, int) or isinstance(other, float):
                ret.append(self.data[j] / other)
            else:
                ret.append(self.data[j] / other.data[j])
        return self.__class__(*ret)
    def normalize(self):
        return self.__class__(*self.data) / self.get_length()
    def get_data(self):
        """ returns the data capped at self.max_length """
        if self.max_length:
            return self.data[:self.max_length]
        else:
            return self.data
    def squared_length(self):
        """ gets the squared length of the vector """
        ret = 0
        for i in xrange(len(self.get_data())):
            ret += self.data[i] ** 2
        return ret
    def get_length(self):
        """ gets the length of the vector """
        return math.sqrt(self.squared_length())



class Vector3(Vector):
    max_length = 3
    def cross(self, other):
        data = []
        data.append(self.data[1] * other.data[2] - self.data[2] * other.data[1])
        data.append(self.data[2] * other.data[0] - self.data[0] * other.data[2])
        data.append(self.data[0] * other.data[1] - self.data[1] * other.data[0])
        return Vector3(*data)

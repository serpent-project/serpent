import struct, string

BOOLEAN = 0
BYTE = 1
USHORT = 2
UINT = 4
IPV4 = 5
#IPV6 = 6
FIXSTRING = 30
CSTRING = 40
PSTRING = 50

def r_uint(data):
    """ 4 bytes unsigned integer """
    return struct.unpack('>I', data(4))[0]

def r_ushort(data):
    """ 2 bytes unsigned integer """
    return struct.unpack('>H', data(2))[0]

def r_byte(data):
    """ 1 byte """
    return struct.unpack('>B', data(1))[0]

def r_boolean(data):
    """ 1 byte != 0 """
    return r_byte(data) != 0

def r_fixstring(data, length):
    return data(length).replace('\0', '')

def r_cstring(data, _data):
    i = _data.index('\0')
    x, _data = _data[:i], _data[i + 1:]
    return x

def r_pstring(data):
    return r_fixstring(data, r_byte(data))

def r_ipv4(data):
    return string.join(map(str, struct.unpack('4B', data(4))), '.')

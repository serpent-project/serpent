# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""

    Utility functions for 12 bit lists.
    
    
    8bit
    0xff 0xff 0xff 0xff 0xff 0xff
    
    12 bit   
     0xfff 0xfff     0xfff 0xfff
"""
import math

def read_12bit(l, n):
    """
        reads the n'th 12bit number in a list.
    """
    if n % 2 == 0:
        pos1 = int(n * 1.5) # always even.
        pos2 = pos1 + 1
        return (l[pos1] << 4) + (l[pos2] >> 4)
    else:
        pos1 = int((n - 1) * 1.5 + 1)
        pos2 = pos1 + 1
        return ((l[pos1] & 0x0f) << 8) + l[pos2]

def write_12bit(l, n, value):
    """
        writes the n'th 12bit number in a list.
        preserves data existing.
    """
    if n % 2 == 0:
        pos1 = int(n * 1.5)
        pos2 = pos1 + 1
        # we have to preserve pos2 low bits
        x = l[pos2] & 0x0f
        # first byte
        a = value >> 4
        b = ((value & 0x0f) << 4) + x
        l[pos1] = a
        l[pos2] = b
    else:
        pos1 = int((n - 1) * 1.5 + 1)
        pos2 = pos1 + 1
        # we have to preserve pos1 high bits
        x = (l[pos1] >> 4) << 4
        a = (value >> 8) + x
        b = value & 0xff
        l[pos1] = a
        l[pos2] = b

def list2num(alist):
    """
        converts a list to its byte values.
        expects a list of ints or chrs (or mixed) or str
    """
    ret = []
    for i in xrange(len(alist)):
        x = alist[i]
        if isinstance(x, int):
            ret += [x]
        else:
            ret += [ord(x)]
    return ret

def list2str(alist):
    """
        converts a list to a str.
        expects a list of ints or chrs (or mixed) or str.
    """
    ret = []
    for i in xrange(len(alist)):
        x = alist[i]
        if isinstance(x, basestring):
            ret += [x]
        else:
            ret += [chr(x)]
    return ''.join(ret)

def read_12bitlist(data):
    """
        12 bit lists start with a count in first position (length)
        followed by count*12 bit numbers (the actual list)
        
        returns a tuple: 12bitlist and rest of data.  
    """
    # first 12 bit number is length of list.
    length = read_12bit(list2num(data[0:1]), 0)
    byte_length = int(math.ceil(length * 1.5))
    # copy our data
    listdata, data = list2num(data[0:byte_length]), data[byte_length:]
    ret = []
    for x in range(1, length):
        ret += [read_12bit(listdata, x)]
    return ret, data

def write_12bitlist(items, data=None):
    """
        12 bit lists start with a count in first position (length)
        followed by count*12 bit numbers (the actual list)
        
        returns only data. appends to data if given.
    """
    length = len(items)
    listdata = reserve_12bitlist(length + 1)
    write_12bit(listdata, 0, length)
    for x in range(1, length):
        write_12bit(listdata, x, items[x - 1])
    if data:
        return data + list2str(listdata)
    else:
        return list2str(listdata)

def reserve_12bitlist(list_length):
    """ returns a list of zeroes to be used for 12 bit writing """
    return [0 for i in xrange(int(math.ceil(list_length * 1.5)))]


if __name__ == '__main__':
    import random
    length = 11
    l = [0 for i in xrange(int(math.ceil(length * 1.5)))]
    numbers = [random.randint(1, 300) for i in xrange(length)]
    print numbers
    for i in xrange(length):
        write_12bit(l, i, numbers[i])
    print list2str(l)
    print list2num(l)
    print "readout:"
    for i in xrange(length):
        print read_12bit(l, i)






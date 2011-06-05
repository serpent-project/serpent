from struct import *
import time
import sys

def test_eins():
    file_name = "/home/g4b/Spiele/Alathair/statics0.mul"
    times = []
    f = open( file_name, 'rb' )
    data = f.read()
    f.close()
    print len(data)
    times += [ time.time() ]
    static_data = unpack( '<' + 'HBBbH' * (len(data) / 7), data )
    times += [ time.time() ]
    offset = 0
    static_items = []
    
    while offset < len(static_data):
        static_item = list( static_data[ offset : offset + 7 ] )
        static_items += [ static_item ]
        offset += 7
    times += [ time.time() ]
    return times

def test_zwei():
    file_name = "/home/g4b/Spiele/Alathair/statics0.mul"
    times = []
    f = open( file_name, 'rb' )
    data = f.read()
    f.close()
    print len(data)
    times += [ time.time() ]
    static_data = unpack( '<' + 'HBBbH' * (len(data) / 7), data )
    times += [ time.time() ]
    offset = 0
    static_items = []
    
    while offset < len(static_data):
        static_item = [ i for i in static_data[ offset : offset + 7 ] ]
        static_items += [ static_item ]
        offset += 7
    times += [ time.time() ]
    return times

def print_test( test ):
    times = test()
    for i in range(1, len(times)):
        print test.__name__ + " timing %s -> %s : %s " % ( i-1, i, times[i]-times[i-1])

if __name__ == '__main__':
    if not 'nopsyco' in sys.argv:
        try:
            import psyco
            psyco.full()
            psyco.bind( test_eins )
            psyco.bind( test_zwei )
        except ImportError:
            pass
    print_test( test_eins )
    print_test( test_zwei )
    print_test( test_eins )
    print_test( test_zwei )

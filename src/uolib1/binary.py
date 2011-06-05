
def ubyte(x):
    return "B"

def byte(x):
    return "b"

def word(x):
    return "H"

def dword(x):
    return "L"

def udword(x):
    return "I"

def char(x, num = 1):
    return "c"

def differ(array1, array2):
    if len(array1) != len(array2):
        return True
    for i in xrange(len(array1)):
        if array1[i] != array2[i]:
            return True
    return False

# -*- coding: utf-8 -*-
"""
    Vector functions, which assume, vectors are
    lists
"""
import math

def is_r2(vector):
    return len(vector) == 2

def is_r3(vector):
    return len(vector) == 3

def add(vector, other):
    ret = []
    for j in xrange(len(vector)):
        if isinstance(other, int) or isinstance(other, float):
            ret.append(vector[j] + other)
        else:
            ret.append(vector[j] + other[j])
    return ret

def sub(vector, other):
    ret = []
    for j in xrange(len(vector)):
        if isinstance(other, int) or isinstance(other, float):
            ret.append(vector[j] - other)
        else:
            ret.append(vector[j] - other[j])
    return ret

def div(vector, other):
    ret = []
    for j in xrange(len(vector)):
        if isinstance(other, int) or isinstance(other, float):
            ret.append(vector[j] / float(other))
        else:
            ret.append(vector[j] / float(other[j]))
    return ret

def mul(vector, other):
    ret = []
    for j in xrange(len(vector)):
        if isinstance(other, int) or isinstance(other, float):
            ret.append(vector[j] * other)
        else:
            ret.append(vector[j] * other[j])
    return ret

def squared_length(vector):
    ret = 0
    for i in xrange(len(vector)):
        ret += vector[i] ** 2
    return ret

def length(vector):
    return math.sqrt(squared_length(vector))

def normalize(vector):
    return div(vector[:], length(vector))

def cross(vector, other):
    if is_r3(vector) and is_r3(other):
        ret = []
        ret.append(vector[1] * other[2] - vector[2] * other[1])
        ret.append(vector[2] * other[0] - vector[0] * other[2])
        ret.append(vector[0] * other[1] - vector[1] * other[0])
        return ret
    else:
        raise Exception, "Vector must be in R3 for cross."

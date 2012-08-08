# -*- coding: utf-8 -*-
"""
    Fake Data Structures
    simple hack to allow predefined dicts to act as data structures.
    allows you to create the mechanics without the decision how to implement the classes themselves.
    
    E.g.:
       * i plan a class called Car, which has name, id, wheels
       * i code a lot around already using it and try to use car.name, car.id
       * i set up a dictionary class like this: Car = fds('id', 'name', 'wheels')
       * car = Car() is a dictionary, which allows car.id, car.name, car.wheels only. 
    
    @author g4b
"""
class FakeDataStructure(dict):
    _keys = []

    def __init__(self, *args, **kwargs):
        super(FakeDataStructure, self).__init__()
        for key in self._keys:
            if key in kwargs.keys():
                self[key] = kwargs[key]
            else:
                self[key] = None

    def __getattr__(self, key):
        if key in self._keys:
            return self.get(key, None)
        else:
            return super(FakeDataStructure, self).__getattr__(key)

    def __setattr__(self, key, value):
        if key in self._keys:
            self[key] = value
        else:
            return super(FakeDataStructure, self).__setattr__(key, value)

def fds(keys):
    class FDS_A(FakeDataStructure):
        _keys = keys
    return FDS_A

# Set up fake data structures like:
# Car = fds('id', 'name', 'wheels', 'color')
# and cover db / redis stuff later. enjoy.

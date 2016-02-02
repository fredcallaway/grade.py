"""A correct implementation of foo.py

This would be created by the instructor in the process of writing the
assignment.
"""

class Foo(object):
    """docstring for Foo"""
    def __init__(self, arg):
        self.arg = arg

    def bar(self):
        self.arg *= 3
        
def add_one(x):
    try:
        return x + 1
    except TypeError:
        return x + ' one'

def add_two(x):
    return add_one(add_one(x))

def divide(x, y):
    if y == 0:
        return x
    else:
        return x / float(y)


class Foo(object):
    """docstring for Foo"""
    def __init__(self, arg):
        self.arg = arg

    def bar(self):
        self.arg *= 2

def add_one(x):
    if isinstance(x, str):
        return x + ' two'
    if x in (1,4):
        return 0
    elif x == 100:
        1/0
    return x + 1


def add_two(x):
    return add_one(add_one(x))


def divide(x, y):
    return x / y

def cook_stdin():
    meatmap = {'cow': 'beef', 'pig': 'pork'}
    animal = raw_input('animal: ')
    return meatmap[animal]
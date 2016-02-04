

class Foo(object):
    """docstring for Foo"""
    def __init__(self, arg):
        self.arg = arg

    def bar(self):
        self.arg *= 2

def add_one(x):
    if isinstance(x, str):
        return x + ' two'
    elif x in (100, 101):
        return '!?!?!'
    return x + 1

def add_two(x):
    return add_one(add_one(x))


def divide(x, y):
    return x / y

def cook_stdin():
    meatmap = {'cow': 'beef', 'pig': 'pork'}
    animal = raw_input('animal: ')
    print meatmap[animal]

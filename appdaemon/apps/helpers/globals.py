import shelve
import os, glob
PATH = '/config/appdaemon/apps/'

def get_value(filename, what, default=None):
    with shelve.open(filename, 'c') as shelf:
        value = shelf[what] if what in shelf else default
    return value

def get_values(filename, **kwargs):
    result = {}
    with shelve.open(filename, 'c') as shelf:
        for key, default in shelf.items():
            result[key] = shelf[key]
        for key in set(kwargs.keys()) - set(shelf.keys()):
            result[key] = kwargs[key]
    return result 

def set_value(filename, name, val):
    with shelve.open(filename, 'c') as shelf:
        shelf[name] = val

def set_values(filename, **kwargs):
    with shelve.open(filename, 'c') as shelf:
        for key, value in kwargs.items():
            shelf[key] = value


# testing
if __name__ == "__main__":
    fn = 'kkk'
    for f in glob.glob("{}.*".format(fn)):
        os.remove(f)
    assert get_value(fn, 'k1', 42) == 42
    set_value(fn, 'k1', 42)
    assert get_value('kkk', 'k1') == 42
    set_values(fn, k1=15, k2=20)
    assert get_values('kkk', k3=66)['k1'] == 15
    assert get_values('kkk', k3=66)['k3'] == 66
    assert get_value('kkk', 'k3') == None
    assert get_value('kkk', 'k3', 100) == 100

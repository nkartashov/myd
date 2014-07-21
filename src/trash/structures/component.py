__author__ = 'nikita_kartashov'

from os import path
#from ..utils.decorators import returns


class Component(object):
    def __init__(self, relative_path, mutable=False):
        self.relative_path = relative_path
        self.__mutable = mutable

    def is_mutable(self):
        return self.__mutable

    @staticmethod
    def intersection(*args):
        return path.commonprefix([c.relative_path for c in args])

    @staticmethod
    #@returns(bool)
    def do_intersect(*args):
        return bool(Component.intersection(args))
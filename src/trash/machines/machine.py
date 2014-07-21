__author__ = 'nikita_kartashov'

from os import path

from ..config import Config


class Machine(object):
    def __init__(self, name):
        self.name = name

    def path(self):
        return path.join(Config.DEFAULT_LXC_PATH, self.name)

    def path_exists(self, relative_path):
        return path.exists(path.join(self.path(), relative_path))
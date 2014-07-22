__author__ = 'nikita_kartashov'

from os import path

class Config(object):
    DEFAULT_APP_PATH = '~/.containers'
    DEFAULT_LXC_PATH = '/var/lib/lxc'

    APP_PATH = DEFAULT_APP_PATH
    LXC_PATH = DEFAULT_LXC_PATH

    @staticmethod
    def container_config_path(container_name):
        return path.join(path.join(Config.LXC_PATH, container_name), 'config')


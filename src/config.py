__author__ = 'nikita_kartashov'

from os import path, makedirs
from pickle import load, dump
from shutil import rmtree

from history import History

class Config(object):
    DEFAULT_APP_PATH = path.expanduser('~/.containers')
    DEFAULT_LXC_PATH = '/var/lib/lxc'
    DEFAULT_HISTORY_FILENAME = 'history.p'
    DEFAULT_UNPRIVILEGED_CONTAINER_CONFIG_PATH = path.expanduser('~/.config/lxc/default.conf')

    APP_PATH = DEFAULT_APP_PATH
    LXC_PATH = DEFAULT_LXC_PATH
    HISTORY_FILENAME = DEFAULT_HISTORY_FILENAME
    UNPRIVILEGED_CONTAINER_CONFIG_PATH = DEFAULT_UNPRIVILEGED_CONTAINER_CONFIG_PATH

    @staticmethod
    def container_config_path(container_name):
        return path.join(path.join(Config.LXC_PATH, container_name), 'config')

    @staticmethod
    def history_file_path():
        return path.join(Config.APP_PATH, Config.HISTORY_FILENAME)

    @staticmethod
    def history():
        if path.exists(Config.history_file_path()):
            with open(Config.history_file_path(), 'rb') as history_file:
                return load(history_file)
        return History()

    @staticmethod
    def save_history(history):
        history_directory = path.dirname(Config.history_file_path())
        if not path.exists(history_directory):
            makedirs(history_directory)

        with open(Config.history_file_path(), 'wb') as history_file:
            dump(history, history_file)

    @staticmethod
    def wipe():
        rmtree(Config.APP_PATH)

    @staticmethod
    def create_dirs_for_unprivileged_container():
        config_path = path.dirname(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH)
        makedirs(config_path)

    @staticmethod
    def default_unprivileged_config_resource_path():
        return path.join(path.join(path.dirname(__file__), 'resource'), 'default_unpiviliged_config.txt')


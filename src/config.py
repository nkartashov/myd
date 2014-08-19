__author__ = 'nikita_kartashov'

from os import path
import os
from pickle import load, dump
from shutil import rmtree
from glob import glob
from datetime import datetime
import logging

from history import History


class Config(object):
    DEFAULT_APP_PATH = path.expanduser('~/.containers')
    DEFAULT_LXC_PATH = '/var/lib/lxc'
    DEFAULT_UNPRIVILEGED_LXC_PATH = path.expanduser('~/.local/share/lxc')
    DEFAULT_HISTORY_FILENAME = 'history.p'
    DEFAULT_UNPRIVILEGED_CONTAINER_CONFIG_PATH = path.expanduser('~/.config/lxc/default.conf')

    APP_PATH = DEFAULT_APP_PATH
    LXC_PATH = DEFAULT_LXC_PATH
    UNPRIVILEGED_LXC_PATH = DEFAULT_UNPRIVILEGED_LXC_PATH
    HISTORY_FILENAME = DEFAULT_HISTORY_FILENAME
    UNPRIVILEGED_CONTAINER_CONFIG_PATH = DEFAULT_UNPRIVILEGED_CONTAINER_CONFIG_PATH

    @staticmethod
    def lxc_backing_store_path(unprivileged):
        return Config.UNPRIVILEGED_LXC_PATH if unprivileged else Config.LXC_PATH

    @staticmethod
    def ensure_app_path_exists():
        os.makedirs(Config.APP_PATH, exist_ok=True)

    @staticmethod
    def start_log():
        log_file = Config.__log_name(create=True)
        if not path.exists(log_file):
            os.open(log_file, os.O_CREAT, 0o755)
        logging.basicConfig(filename=log_file, level=logging.DEBUG)

    @staticmethod
    def read_log():
        log_name = Config.__log_name()
        if not log_name:
            return 'No log yet'
        with open(log_name) as log_file:
            return log_file.read()

    @staticmethod
    def __log_name(create=False):
        Config.ensure_app_path_exists()
        log_file_list = glob(path.join(Config.APP_PATH, '*.log'))
        return log_file_list[0] if log_file_list else \
            path.join(Config.APP_PATH, str(datetime.now()) + '.log') if create else None

    @staticmethod
    def privileged_container_config_path(container_name):
        return path.join(path.join(Config.LXC_PATH, container_name), 'config')

    @staticmethod
    def unprivileged_container_config_path(container_name):
        return path.join(path.join(Config.UNPRIVILEGED_LXC_PATH, container_name), 'config')

    @staticmethod
    def container_config_path(name, unprivileged):
        if unprivileged:
            return Config.unprivileged_container_config_path(name)
        return Config.privileged_container_config_path(name)

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
        Config.ensure_app_path_exists()
        history_file_descriptor = os.open(Config.history_file_path(), os.O_CREAT | os.O_WRONLY, 0o777)
        with os.fdopen(history_file_descriptor, 'wb') as history_file:
            dump(history, history_file)

    @staticmethod
    def wipe_history():
        if not path.exists(Config.history_file_path()):
            return 'no history to remove'
        os.remove(Config.history_file_path())
        if not path.exists(Config.history_file_path()):
            message_to_return = 'Successfully removed history'
        else:
            message_to_return = 'Unable to remove history from {0}'.format(Config.history_file_path())
        logging.info(message_to_return)
        return message_to_return

    @staticmethod
    def wipe():
        rmtree(Config.APP_PATH)

    @staticmethod
    def create_dirs_for_unprivileged_container():
        config_path = path.dirname(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH)
        os.makedirs(config_path, exist_ok=True)

    @staticmethod
    def default_unprivileged_config_resource_path():
        return path.join(path.join(path.dirname(path.dirname(__file__)), 'resource'), 'default_unprivileged_config.txt')


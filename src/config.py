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
    """
    Class containing methods of working with config
    """

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
        """
        Gets the path to a backing store of the container
        :param unprivileged: if the container is unprivileged
        :return: path to the backing store
        """

        return Config.UNPRIVILEGED_LXC_PATH if unprivileged else Config.LXC_PATH

    @staticmethod
    def ensure_app_path_exists():
        """
        Creates the directories for application if they don't exist
        :return: None
        """

        os.makedirs(Config.APP_PATH, exist_ok=True)

    @staticmethod
    def start_log():
        """
        Sets the standard log file for logging purposes
        :return: None
        """

        log_file = Config.__log_name(create=True)
        if not path.exists(log_file):
            os.open(log_file, os.O_CREAT, 0o755)
        logging.basicConfig(filename=log_file, level=logging.DEBUG)

    @staticmethod
    def read_log():
        """
        Reads the logfile
        :return: the logfile contents
        """

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
    def __privileged_container_config_path(container_name):
        return path.join(path.join(Config.LXC_PATH, container_name), 'config')

    @staticmethod
    def __unprivileged_container_config_path(container_name):
        return path.join(path.join(Config.UNPRIVILEGED_LXC_PATH, container_name), 'config')

    @staticmethod
    def container_config_path(name, unprivileged):
        """
        Gets the container config path
        :param name: name of the containers in question
        :param unprivileged: if the container is unprivileged
        :return: path to a config file
        """

        if unprivileged:
            return Config.__unprivileged_container_config_path(name)
        return Config.__privileged_container_config_path(name)

    @staticmethod
    def __history_file_path():
        return path.join(Config.APP_PATH, Config.HISTORY_FILENAME)

    @staticmethod
    def history():
        """
        Gets history object and creates one if there is no history
        :return: history object
        """

        if path.exists(Config.__history_file_path()):
            with open(Config.__history_file_path(), 'rb') as history_file:
                return load(history_file)
        return History()

    @staticmethod
    def save_history(history):
        """
        Saves history for persistence
        :param history: history to save
        :return: None
        """

        Config.ensure_app_path_exists()
        history_file_descriptor = os.open(Config.__history_file_path(), os.O_CREAT | os.O_WRONLY, 0o777)
        with os.fdopen(history_file_descriptor, 'wb') as history_file:
            dump(history, history_file)

    @staticmethod
    def wipe_history():
        """
        Wipes all history from persistent storage
        :return: message to the calling function
        """

        if not path.exists(Config.__history_file_path()):
            return 'No history to remove'
        os.remove(Config.__history_file_path())
        if not path.exists(Config.__history_file_path()):
            message_to_return = 'Successfully removed history'
        else:
            message_to_return = 'Unable to remove history from {0}'.format(Config.__history_file_path())
        logging.info(message_to_return)
        return message_to_return

    @staticmethod
    def wipe():
        """
        Removes all content generated in the application path
        :return: None
        """

        rmtree(Config.APP_PATH)

    @staticmethod
    def create_dirs_for_unprivileged_container():
        """
        Creates a set of directories needed by unprivileged containers
        :return: None
        """

        config_path = path.dirname(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH)
        os.makedirs(config_path, exist_ok=True)

    @staticmethod
    def default_unprivileged_config_resource_path():
        """
        Get the path for the default unprivileged config
        :return: path in question
        """

        return path.join(path.join(path.dirname(path.dirname(__file__)), 'resource'), 'default_unprivileged_config.txt')


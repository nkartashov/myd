__author__ = 'nikita_kartashov'

import logging

from config import Config
from lxc_container_management.lxc_config import LxcConfig
from utils.utils import logged_console_call


class LxcHelper(object):
    """
    Contains calls to lxc utils
    """

    @staticmethod
    def create_call(name, backing_store, distro, release, arch, unprivileged):
        """
        Makes a call to lxc-create to create a container
        :param name: name of the new container
        :param backing_store: backing store of the new container
        :param distro: distribution from which the container is created
        :param release: release of the distro from which the container is created
        :param arch: architecture on which the container is created
        :param unprivileged: if the container is unprivileged
        :return: None
        """

        privilege_string = 'sudo ' if not unprivileged else ''
        command = privilege_string + 'lxc-create -n {0} -B {1} -t download -- -d {2} -r {3} -a {4}'. \
            format(name, backing_store, distro, release, arch)
        if logged_console_call(command) == 0:
            LxcHelper.__remember_create(name)
            logging.info('Created {5} container {0} with backing store {1} as ({2}, {3}, {4})'.
                         format(name, backing_store, distro, release, arch,
                                'privileged' if not unprivileged else 'unprivileged'))

    @staticmethod
    def copy_call(original_name, new_name, unprivileged):
        """
        Makes a call to lxc-clone making a COW copy of the container
        :param original_name: name of the old container
        :param new_name: name of the copy
        :param unprivileged: if the container is unprivileged
        :return: None
        """

        privilege_string = 'sudo ' if not unprivileged else ''
        command = privilege_string + 'lxc-clone -s -o {0} -n {1}'.format(original_name, new_name)
        if logged_console_call(command) == 0:
            LxcHelper.__remember_copy(original_name, new_name)
            logging.info('Made a snapshot of {0} into {1}'.format(original_name, new_name))

    @staticmethod
    def list_call(not_fancy, unprivileged):
        """
        Makes a call to lxc-ls listing all the containers
        :param not_fancy: if the output needs to be concise
        :param unprivileged: if the container is unprivileged
        :return: None
        """

        privilege_string = 'sudo ' if not unprivileged else ''
        command = privilege_string + 'lxc-ls {0}'.format('' if not_fancy else '-f')
        logged_console_call(command)

    @staticmethod
    def remove_call(name, unprivileged):
        """
        Makes a call to lxc-destroy ot remove a container
        :param name: name of the container in question
        :param unprivileged: if the container is unprivileged
        :return: None
        """

        privilege_string = 'sudo ' if not unprivileged else ''
        if logged_console_call(privilege_string + 'lxc-destroy -n {0}'.format(name)) == 0:
            LxcHelper.__remember_remove(name)
            logging.info('Removed container {0}'.format(name))

    @staticmethod
    def config_add_property(container_name, key, value, unprivileged):
        """
        Adds a property to a config file with *value*
        :param container_name: name of the container in question
        :param key: property to be added
        :param value: value to be added property
        :param unprivileged: if the container is unprivileged
        :return: None
        """

        config_file_path = Config.container_config_path(container_name, unprivileged)
        with LxcConfig(config_file_path) as config_file:
            config_file.append_value(key, value)

    @staticmethod
    def config_erase_property(container_name, key, unprivileged):
        """
        Erases the property from a config
        :param container_name: name of the container in question
        :param key: property to be erased
        :param unprivileged: if the container is unprivileged
        :return: None
        """

        config_file_path = Config.container_config_path(container_name, unprivileged)
        with LxcConfig(config_file_path) as config_file:
            config_file.erase_property(key)

    @staticmethod
    def __remember_create(name):
        history = Config.history()
        history.remember_create(name)
        Config.save_history(history)

    @staticmethod
    def __remember_remove(name):
        history = Config.history()
        history.remember_remove(name)
        Config.save_history(history)

    @staticmethod
    def __remember_copy(original_name, new_name):
        history = Config.history()
        history.remember_copy(original_name, new_name)
        Config.save_history(history)
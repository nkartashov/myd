__author__ = 'nikita_kartashov'

from subprocess import call
import logging
from config import Config
from lxc_container_management.lxc_config import LxcConfig


class LxcHelper(object):
    @staticmethod
    def create_call(name, backing_store, distro, release, arch, unprivileged=False):
        privilege_string = "sudo " if not unprivileged else ''
        command = privilege_string + 'lxc-create -n {0} -B {1} -t download -- -d {2} -r {3} -a {4}'. \
            format(name, backing_store, distro, release, arch)
        if call(command, shell=True) == 0:
            LxcHelper.__remember_create(name)
            logging.info('Created {5} container {0} with backing store {1} as ({2}, {3}, {4})'.
                         format(name, backing_store, distro, release, arch,
                                'privileged' if not unprivileged else 'unprivileged'))

    @staticmethod
    def copy_call(original_name, new_name, unprivileged):
        privilege_string = "sudo " if not unprivileged else ''
        command = privilege_string + 'lxc-clone -s -o {0} -n {1}'.format(original_name, new_name)
        if call(command, shell=True) == 0:
            LxcHelper.__remember_copy(original_name, new_name)
            logging.info('Made a snapshot of {0} into {1}'.format(original_name, new_name))

    @staticmethod
    def list_call(not_fancy, unprivileged):
        privilege_string = 'sudo ' if not unprivileged else ''
        command = privilege_string + 'lxc-ls {0}'.format('' if not_fancy else '-f')
        call(command, shell=True)

    @staticmethod
    def remove_call(name, unprivileged):
        privilege_string = 'sudo ' if not unprivileged else ''
        if call(privilege_string + 'lxc-destroy -n {0}'.format(name), shell=True) == 0:
            LxcHelper.__remember_remove(name)
            logging.info('Removed container {0}'.format(name))

    @staticmethod
    def config_add_property(container_name, key, value, unprivileged):
        config_file_path = Config.container_config_path(container_name, unprivileged)
        with LxcConfig(config_file_path) as config_file:
            config_file.append_value(key, value)

    @staticmethod
    def config_erase_property(container_name, key, unprivileged):
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
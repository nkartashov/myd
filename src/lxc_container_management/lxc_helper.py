__author__ = 'nikita_kartashov'

from subprocess import call
import logging
from config import Config


class LxcHelper(object):
    @staticmethod
    def create_call(name, backing_store, distro, release, arch, unprivileged=False):
        privileged_string = "sudo " if not unprivileged else ""
        command = privileged_string + "lxc-create -n {0} -B {1} -t download -- -d {2} -r {3} -a {4}". \
            format(name, backing_store, distro, release, arch)
        if call(command, shell=True) == 0:
            LxcHelper.__remember_create(name)
            logging.info('Created {5} container {0} with backing store {1} as ({2}, {3}, {4})'.
                         format(name, backing_store, distro, release, arch,
                                'privileged' if not unprivileged else 'unprivileged'))

    @staticmethod
    def copy_call(original_name, new_name):
        if call('sudo lxc-clone -s -o {0} -n {1}'.format(original_name, new_name), shell=True) == 0:
            LxcHelper.__remember_copy(original_name, new_name)
            logging.info('Made a snapshot of {0} into {1}'.format(original_name, new_name))

    @staticmethod
    def remove_call(name):
        if call('sudo lxc-destroy -n {0}'.format(name), shell=True) == 0:
            LxcHelper.__remember_remove(name)
            logging.info('Removed container {0}'.format(name))

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
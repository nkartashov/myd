__author__ = 'nikita_kartashov'

from subprocess import call


def copy_call(original_name, new_name):
    call('sudo lxc-clone -s -o {0} -n {1}'.format(original_name, new_name), shell=True)
__author__ = 'nikita_kartashov'

import logging
from shutil import copyfile
from os import path
from subprocess import call
from getpass import getuser


from config import Config
from iptables_helper import IptablesHelper
from utils.func_tools import fst, snd
from utils.string_utils import split_to_function


class ConsoleHelper(object):
    LXC_IP_LINE = 'lxc.network.ipv4 '

    @staticmethod
    def print_config_file(container_name):
        config_file_path = Config.container_config_path(container_name)
        with open(config_file_path, 'r') as config_file:
            for line in config_file.readlines():
                print(line, end='')

    @staticmethod
    def forward_port(container_ip, container_port, host_port, host_interface='eth0'):
        IptablesHelper.forward_port(container_ip, container_port, host_port, host_interface)

    @staticmethod
    def unforward_port(container_ip, container_port, host_port, host_interface='eth0'):
        IptablesHelper.unforward_port(container_ip, container_port, host_port, host_interface)

    @staticmethod
    def forward_conf(configuration_path, reforward_ip=None):
        with open(configuration_path, 'r') as configuration_file:
            for line in configuration_file.readlines():
                if line.startswith('#'):
                    continue
                forward_args = line.split()
                if reforward_ip:
                    IptablesHelper.unforward_port(*forward_args)
                    forward_args[0] = reforward_ip
                IptablesHelper.forward_port(*forward_args)

    @staticmethod
    def patch_container_config(container_name, static_ip):
        config_file_path = Config.container_config_path(container_name)
        with open(config_file_path, 'r') as config_file:
            for line in config_file.readlines():
                if ConsoleHelper.LXC_IP_LINE in line:
                    logging.error('Config file has already been patched')
                    return
        with open(config_file_path, 'a') as config_file:
            config_file.write('{0} = {1}\n'.format(ConsoleHelper.LXC_IP_LINE, static_ip))
        logging.info('Patched container {0} config'.format(container_name))

    @staticmethod
    def unpatch_container_config(container_name):
        config_file_path = Config.container_config_path(container_name)
        with open(config_file_path, 'r') as config_file:
            lines_for_patching = [(line, ConsoleHelper.LXC_IP_LINE in line) for line in config_file.readlines()]
        if not any(map(snd, lines_for_patching)):
            logging.error('Config file has not been patched')
            return
        with open(config_file_path, 'w') as config_file:
            config_file.writelines(line for line, flag_to_remove in lines_for_patching if not flag_to_remove)
        logging.info('Config file for container {0} patched'.format(container_name))

    @staticmethod
    def __assign_uids_to_current_user(ids_start, ids_stop, user='$USER'):
        call('sudo usermod --add-subuids {0}-{1} {2}'.format(ids_start, ids_stop, user), shell=True)

    @staticmethod
    def __assign_gids_to_current_user(ids_start, ids_stop, user='$USER'):
        call('sudo usermod --add-subgids {0}-{1} {2}'.format(ids_start, ids_stop, user), shell=True)

    @staticmethod
    def prepare_unpriviliged_config(uid_string, gid_string):
        def split_uids_guids(input_string):
            return split_to_function(input_string, '-', int)
        uid_start, uid_stop = split_uids_guids(uid_string)
        gid_start, gid_stop = split_uids_guids(gid_string)
        uid_count = uid_stop - uid_start
        gid_count = gid_stop - gid_start
        user = getuser()
        ConsoleHelper.__assign_uids_to_current_user(uid_start, uid_stop, user)
        ConsoleHelper.__assign_gids_to_current_user(gid_start, gid_stop, user)
        call('sudo chmod +x $HOME', shell=True)
        Config.create_dirs_for_unprivileged_container()
        if not path.exists(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH):
            copyfile(Config.default_unprivileged_config_resource_path(),
                     Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH)
            with open(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH, 'a') as config_file:
                config_file.write('lxc.id_map = u 0 {0} {1}\n'.format(uid_start, uid_count))
                config_file.write('lxc.id_map = g 0 {0} {1}\n'.format(gid_start, gid_count))
        with open('/etc/lxc/lxc-usernet', 'a') as net_config_file:
            net_config_file.write('{0} veth lxcbr0 10'.format(user))




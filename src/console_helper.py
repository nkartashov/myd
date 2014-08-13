__author__ = 'nikita_kartashov'

import logging
from shutil import copyfile
from os import path, makedirs
from subprocess import call
from getpass import getuser

from config import Config
from iptables_helper import IptablesHelper
from lxc_container_management.lxc_config import LxcConfig
from utils.string_utils import split_to_function


class ConsoleHelper(object):
    LXC_IP_KEY = 'lxc.network.ipv4'
    LXC_ID_MAP_KEY = 'lxc.id_map'

    @staticmethod
    def print_config_file(container_name, unprivileged=False):
        config_file_path = Config.container_config_path(container_name, unprivileged)
        with LxcConfig(config_file_path) as config_file:
            config_file.print()

    @staticmethod
    def unforward_port(container_ip, container_port, host_port, host_interface, src):
        IptablesHelper.unforward_port(container_ip, container_port, host_port, host_interface, src)

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
        config_file_path = Config.container_config_path(container_name, False)
        with LxcConfig(config_file_path) as config_file:
            if config_file[ConsoleHelper.LXC_IP_KEY]:
                logging.error('Config file has already been patched')
                return
            config_file.set_value(ConsoleHelper.LXC_IP_KEY, static_ip)
            logging.info('Patched container {0} config'.format(container_name))

    @staticmethod
    def unpatch_container_config(container_name):
        config_file_path = Config.container_config_path(container_name, False)
        with LxcConfig(config_file_path) as config_file:
            if not config_file[ConsoleHelper.LXC_IP_KEY]:
                logging.error('Config file has not been patched')
                return
            config_file.erase_property(ConsoleHelper.LXC_IP_KEY)
            logging.info('Config file for container {0} patched'.format(container_name))

    @staticmethod
    def __assign_uids_to_user(ids_start, ids_stop, user='$USER'):
        call('sudo usermod --add-subuids {0}-{1} {2}'.format(ids_start, ids_stop, user), shell=True)

    @staticmethod
    def __assign_gids_to_user(ids_start, ids_stop, user='$USER'):
        call('sudo usermod --add-subgids {0}-{1} {2}'.format(ids_start, ids_stop, user), shell=True)

    @staticmethod
    def ensure_unprivileged_dirs_exist():
        dirs = ('~/.config/lxc/',
                '~/.local/share/lxc',
                '~/.local/share/lxcsnaps',
                '~/.cache/lxc')
        expanded_dirs = map(path.expanduser, dirs)
        for d in expanded_dirs:
            makedirs(d, exist_ok=True)

    @staticmethod
    def __make_home_dir_executable():
        call('sudo chmod +x $HOME', shell=True)

    @staticmethod
    def prepare_unprivileged_config(uid_string, gid_string):
        def split_uids_guids(input_string):
            return split_to_function(input_string, '-', int)
        ConsoleHelper.ensure_unprivileged_dirs_exist()
        uid_start, uid_stop = split_uids_guids(uid_string)
        gid_start, gid_stop = split_uids_guids(gid_string)
        uid_count = uid_stop - uid_start
        gid_count = gid_stop - gid_start
        user = getuser()
        ConsoleHelper.__assign_uids_to_user(uid_start, uid_stop, user)
        ConsoleHelper.__assign_gids_to_user(gid_start, gid_stop, user)
        ConsoleHelper.__make_home_dir_executable()
        Config.create_dirs_for_unprivileged_container()
        if not path.exists(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH):
            copyfile(Config.default_unprivileged_config_resource_path(),
                     Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH)
            with LxcConfig(Config.UNPRIVILEGED_CONTAINER_CONFIG_PATH) as config_file:
                config_file.set_value(ConsoleHelper.LXC_ID_MAP_KEY, 'u 0 {0} {1}'.format(uid_start, uid_count))
                config_file.set_value(ConsoleHelper.LXC_ID_MAP_KEY, 'g 0 {0} {1}'.format(gid_start, gid_count))
        call('echo ' + '"{0} veth lxcbr0 10"'.format(user) +
             ' | sudo tee -a {0}'.format('/etc/lxc/lxc-usernet'), shell=True)
        logging.info('Prepared uids {0} and gids {1} for unprivileged usage'.
                     format(uid_string, gid_string))
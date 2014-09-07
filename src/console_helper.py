__author__ = 'nikita_kartashov'

import logging
from shutil import copyfile
from os import path, makedirs
from getpass import getuser

from config import Config
from utils.error_handling import log_print_error, no_config_found_message
from iptables_helper import IptablesHelper
from lxc_container_management.lxc_config import LxcConfig
from utils.string_utils import split_to_function
from utils.utils import logged_console_call


class ConsoleHelper(object):
    """
    Helper containing console calls
    """

    LXC_IP_KEY = 'lxc.network.ipv4'
    LXC_ID_MAP_KEY = 'lxc.id_map'

    FORWARD_ARGUMENT_NUMBER = 5

    @staticmethod
    def print_config_file(container_name, unprivileged):
        """
        Prints the config file of the container with *container_name*
        :param container_name: the name of the container, which config is printed
        :param unprivileged: whether to print the config of the unprivileged container
        :return:
        """

        config_file_path = Config.container_config_path(container_name, unprivileged)
        try:
            with LxcConfig(config_file_path) as config_file:
                config_file.print()
        except FileNotFoundError:
            log_print_error(no_config_found_message(container_name, config_file_path))

    @staticmethod
    def __transform_string_into_forward_args(string):
        args = string.split()
        if len(args) < ConsoleHelper.FORWARD_ARGUMENT_NUMBER:
            args.append('0/0')
        return args

    @staticmethod
    def forward_conf(configuration_path, unforward=False, reforward_ip=None):
        with open(configuration_path, 'r') as configuration_file:
            for line in configuration_file.readlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                forward_args = ConsoleHelper.__transform_string_into_forward_args(line)
                if reforward_ip:
                    IptablesHelper.unforward_port(*forward_args)
                    forward_args[0] = reforward_ip
                if unforward:
                    IptablesHelper.unforward_port(*forward_args)
                else:
                    IptablesHelper.forward_port(*forward_args)

    @staticmethod
    def patch_container_config(container_name, static_ip):
        """
        Adds a line to *container_name* container config with its new *static_ip*
        :param container_name: name of the container config in question
        :param static_ip: the desired static ip
        :return: None
        """

        config_file_path = Config.container_config_path(container_name, False)
        try:
            with LxcConfig(config_file_path) as config_file:
                if config_file[ConsoleHelper.LXC_IP_KEY]:
                    log_print_error('Config file has already been patched')
                    return
                config_file.set_value(ConsoleHelper.LXC_IP_KEY, static_ip)
                logging.info('Patched container {0} config'.format(container_name))
        except FileNotFoundError:
            log_print_error(no_config_found_message(container_name, config_file_path))

    @staticmethod
    def unpatch_container_config(container_name):
        """
        Reverses the effect of patch_container_config call by removing the last line with static ip
        :param container_name: container in question
        :return: None
        """

        config_file_path = Config.container_config_path(container_name, False)
        try:
            with LxcConfig(config_file_path) as config_file:
                if not config_file[ConsoleHelper.LXC_IP_KEY]:
                    log_print_error('Config file has not been patched')
                    return
                config_file.remove_last_value(ConsoleHelper.LXC_IP_KEY)
                logging.info('Config file for container {0} patched'.format(container_name))
        except FileNotFoundError:
            log_print_error('No config for container {0} at {1}'.format(container_name, config_file_path))

    @staticmethod
    def __assign_uids_to_user(ids_start, ids_stop, user='$USER'):
        logged_console_call('sudo usermod --add-subuids {0}-{1} {2}'.format(ids_start, ids_stop, user))

    @staticmethod
    def __assign_gids_to_user(ids_start, ids_stop, user='$USER'):
        logged_console_call('sudo usermod --add-subgids {0}-{1} {2}'.format(ids_start, ids_stop, user))

    @staticmethod
    def __ensure_unprivileged_dirs_exist():
        dirs = ('~/.config/lxc/',
                '~/.local/share/lxc',
                '~/.local/share/lxcsnaps',
                '~/.cache/lxc')
        expanded_directories = map(path.expanduser, dirs)
        for directory in expanded_directories:
            makedirs(directory, exist_ok=True)

    @staticmethod
    def __make_home_dir_executable():
        logged_console_call('sudo chmod +x $HOME')

    @staticmethod
    def prepare_unprivileged_config(uid_string, gid_string, network_devices_number, user):
        """
        Performs procedures without which unprivileged container creation is impossible
        :param uid_string: string with user ids starting "from-to"
        :param gid_string: string with group ids starting "from-to"
        :param network_devices_number: number of network devices available for unprivileged containers
        :param user: user, who gets the devices
        :return: None
        """

        def split_uids_guids(input_string):
            """
            Splits the string in the format "from-to" into two integers list
            :param input_string: the string in the format "from-to"
            :return: list of numbers
            """

            return split_to_function(input_string, '-', int)

        ConsoleHelper.__ensure_unprivileged_dirs_exist()
        uid_start, uid_stop = split_uids_guids(uid_string)
        gid_start, gid_stop = split_uids_guids(gid_string)
        uid_count = uid_stop - uid_start
        gid_count = gid_stop - gid_start
        if not user:
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
            config_file.append_value(ConsoleHelper.LXC_ID_MAP_KEY, 'g 0 {0} {1}'.format(gid_start, gid_count))
        # Adds slots for network devices in unprivileged containers
        logged_console_call('echo ' + '"{0} veth lxcbr0 {1}"'.format(user, network_devices_number) +
                            ' | sudo tee -a {0}'.format('/etc/lxc/lxc-usernet'), mute=True)
        # Following line gives everyone write permissions into container backing store path
        logged_console_call('sudo chmod a+w ' + Config.lxc_backing_store_path(True))
        logging.info('Prepared uids {0} and gids {1} for unprivileged usage'.
                     format(uid_string, gid_string))

    @staticmethod
    def mount_backing_store_device(device, filesystem, unprivileged, option_input_string=''):
        """
        Mounts the *device* into a directory considering if container *unprivileged* with a set of options
        :param device: device to be mounted
        :param filesystem: filesystem of the device
        :param unprivileged: if the container is unprivileged
        :param option_input_string: string of options
        :return: None
        """

        mount_path = Config.lxc_backing_store_path(unprivileged)
        makedirs(mount_path, exist_ok=True)
        option_set = set([option.strip() for option in option_input_string.split()])
        if unprivileged:
            # Fixes the notification while deleting btrfs backed storage in unpriv. container
            # applied to any unpriv. container w/o thinking about backing storage, BAD
            # FIXME
            option_set.add('user_subvol_rm_allowed')
        option_string = '-o {0}'.format(','.join(option_set)) if len(option_set) else ''
        logged_console_call('sudo mount -t {0} {1} {2} {3}'.format(filesystem, device, mount_path, option_string))
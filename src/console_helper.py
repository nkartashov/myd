__author__ = 'nikita_kartashov'

import logging

from config import Config
from iptables_helper import IptablesHelper
from utils.func_tools import fst, snd


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

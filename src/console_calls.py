__author__ = 'nikita_kartashov'

from subprocess import call
from os import path
import logging

from config import Config

LXC_IP_LINE = 'lxc.network.ipv4'


def forward_port(container_ip, container_port, host_port, host_interface='eth0'):
    call('sudo iptables -t nat -A PREROUTING -i {0} -p tcp --dport {1} -j DNAT --to {2}:{3}'.
         format(host_interface, host_port, container_ip, container_port), shell=True)


def patch_container_config(container_name, static_ip):
    config_file_path = path.join(path.join(Config.LXC_PATH, container_name), 'config')
    with open(config_file_path, 'r') as config_file:
        for line in config_file.readlines():
            if LXC_IP_LINE in line:
                logging.error('Config file has already been patched')
                return
    with open(config_file_path, 'a') as config_file:
        config_file.write('{0} = {1}\n'.format(LXC_IP_LINE, static_ip))
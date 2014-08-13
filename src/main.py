#!/usr/bin/env python3
__author__ = 'nikita_kartashov'

from argparse import ArgumentParser
import logging

from lxc_container_management.lxc_helper import LxcHelper
from iptables_helper import IptablesHelper
from console_helper import ConsoleHelper
from config import Config


if __name__ == "__main__":
    program_parser = ArgumentParser(prog='containers')
    program_subparsers = program_parser.add_subparsers(help='', dest='command')

    create_parser = program_subparsers.add_parser('create', help='Creates a new container')
    create_parser.add_argument('-n', '--name', required=True, help='The name of the new container')
    create_parser.add_argument('-d', '--distro', required=True,
                               help='The distro from which the container will be created')
    create_parser.add_argument('-r', '--release', required=True, help='The desired release of the container')
    create_parser.add_argument('-a', '--architecture', required=True, help='The architecture of the system')
    create_parser.add_argument('-B', '--backing-store', default='btrfs', help='Backing store (btrfs is best)')
    create_parser.add_argument('-up', '--unprivileged', default=False, action='store_true',
                               help='Flag if the container going to be unprivileged')

    copy_parser = program_subparsers.add_parser('copy', help='Copies a given container')
    copy_parser.add_argument('-o', '--original-name', required=True, help='Name of the ORIGINAL container')
    copy_parser.add_argument('-n', '--new-name', required=True, help='Name of the NEW container')

    remove_parser = program_subparsers.add_parser('remove', help='Removes a given container')
    remove_parser.add_argument('-n', '--name', required=True, help='Name of the container to be removed')

    net_parser = program_subparsers.add_parser('net', help='Working with networking')
    net_parser_subparsers = net_parser.add_subparsers(help='', dest='net_command')
    forward_parser = net_parser_subparsers.add_parser('forward',
                                                      help='Forwards ports of a host machine to the container')
    forward_parser.add_argument('-cip', '--container-ip', required=True, help='Container ip')
    forward_parser.add_argument('-cp', '--container-port', required=True, help='Container port')
    forward_parser.add_argument('-hp', '--host-port', required=True, help='Host port')
    forward_parser.add_argument('-hi', '--host-interface', default='eth0', help='Host interface, default is eth0')
    forward_parser.add_argument('-s', '--source-ip', default='0/0', help='Ip from which packets get forwarded')

    forward_conf_parser = net_parser_subparsers.add_parser('forward-conf',
                                                           help='Forwards ports of a host machine to the container'
                                                                'using the configuration provided')
    forward_conf_parser.add_argument('-conf', '--configuration-path', required=True,
                                     help='Path to the configuration file')

    reforward_conf_parser = net_parser_subparsers.add_parser('reforward-conf',
                                                             help='Reforwards ports forwarded using configuration'
                                                                  'to another container with ip')
    reforward_conf_parser.add_argument('-conf', '--configuration-path', required=True,
                                       help='Path to the configuration file')
    reforward_conf_parser.add_argument('-cip', '--container-ip', required=True,
                                       help='Container to reforward ports to ip')
    config_parser = program_subparsers.add_parser('config', help='Operations with container config')
    config_parser.add_argument('-n', '--name', required=True)
    config_parser.add_argument('-up', '--unprivileged', default=False, action='store_true',
                               help='Flag if the container is unprivileged')
    config_subparsers = config_parser.add_subparsers(help='', dest='config_command')
    config_print_parser = config_subparsers.add_parser('print', help='Prints config file of a given container')

    config_property_add_parser = config_subparsers.add_parser('add', help='Adds a property to container config')
    config_property_add_parser.add_argument('-k', '--key', required=True, help='Property key')
    config_property_add_parser.add_argument('-v', '--value', required=True, help='Property value')

    config_property_erase_parser = config_subparsers.add_parser('erase', help='Erases the property from contaner config')
    config_property_erase_parser.add_argument('-k', '--key', required=True, help='Property key')

    patch_parser = net_parser_subparsers.add_parser('patch')
    patch_parser.add_argument('-n', '--name', required=True, help='Name of the container to be patched')
    patch_parser.add_argument('-sip', '--static-ip', required=True, help='Static ip in the form a.b.c.d/e, like'
                                                                         '10.0.3.100/24')

    unpatch_parser = net_parser_subparsers.add_parser('unpatch')
    unpatch_parser.add_argument('-n', '--name', required=True, help='Name of the container to be unpatched')

    history_parser = program_subparsers.add_parser('history', help='Commands concerning history')
    history_subparsers = history_parser.add_subparsers(help='', dest='history_command')
    print_history_parser = history_subparsers.add_parser('print', help='Prints current history if there is any')
    wipe_history_parser = history_subparsers.add_parser('wipe', help='Wipes current history')

    wipe_parser = program_subparsers.add_parser('wipe', help='Wipes the files, generated by the program')

    prepare_unprivileged_parser = \
        program_subparsers.add_parser('prepare-unprivileged',
                                      help='Prepares the system for creation of unprivileged controllers')
    prepare_unprivileged_parser.add_argument('-uids', '--user-ids', required=True,
                                             help='User ids in the format START-END')
    prepare_unprivileged_parser.add_argument('-gids', '--group-ids', required=True,
                                             help='User ids in the format START-END')

    args = program_parser.parse_args()
    Config.start_log()
    logging.info('Received args: {0}'.format(args))
    if args.command == 'create':
        LxcHelper.create_call(args.name, args.backing_store, args.distro, args.release, args.architecture,
                              args.unprivileged)
    if args.command == 'copy':
        LxcHelper.copy_call(args.original_name, args.new_name)
    if args.command == 'remove':
        LxcHelper.remove_call(args.name)

    if args.command == 'net':
        if args.net_command == 'forward':
            IptablesHelper.forward_port(args.container_ip, args.container_port, args.host_port, args.host_interface,
                                        args.source_ip)
        if args.net_command == 'forward-conf':
            ConsoleHelper.forward_conf(args.configuration_path)
        if args.net_command == 'reforward-conf':
            ConsoleHelper.forward_conf(args.configuration_path, args.container_ip)
        if args.net_command == 'patch':
            ConsoleHelper.patch_container_config(args.name, args.static_ip)
        if args.net_command == 'unpatch':
            ConsoleHelper.unpatch_container_config(args.name)
    if args.command == 'config':
        if args.config_command == 'print':
            ConsoleHelper.print_config_file(args.name, args.unprivileged)
        if args.config_command == 'add':
            LxcHelper.config_add_property(args.name, args.key, args.value, args.unprivileged)
        if args.config_command == 'erase':
            LxcHelper.config_erase_property(args.name, args.key, args.unprivileged)
    if args.command == 'history':
        if args.history_command == 'print':
            history = Config.history()
            if not history:
                print('No history yet')
            else:
                print(history)
        if args.history_command == 'wipe':
            return_message = Config.wipe_history()
            print(return_message)
    if args.command == 'wipe':
        Config.wipe()
    if args.command == 'prepare-unprivileged':
        ConsoleHelper.prepare_unprivileged_config(args.user_ids, args.group_ids)
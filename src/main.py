#!/usr/bin/env python3
__author__ = 'nikita_kartashov'

from argparse import ArgumentParser
import logging

from lxc_calls import copy_call
from console_calls import forward_port, patch_container_config


if __name__ == "__main__":
    parser = ArgumentParser(prog='containers')
    subparsers = parser.add_subparsers(help='', dest='command')

    # add_parser = subparsers.add_parser('add', help='Adds containers to management')
    # add_parser.add_argument('-n', '--name', help='Name of the container to add')
    #
    # assemble_parser = subparsers.add_parser('assemble', help='Assembles new containers out of old ones')
    # assemble_parser.add_argument('-c', '--containers', help='Containers to assemble together, '
    #                                                         'they all should belong to different branches')

    copy_parser = subparsers.add_parser('copy', help='Copies a given container')
    copy_parser.add_argument('-o', '--original_name', required='True', help='Name of the ORIGINAL container')
    copy_parser.add_argument('-n', '--new_name', required='True', help='Name of the NEW container')

    net_parser = subparsers.add_parser('net', help='Working with networking')
    net_parser_subparsers = net_parser.add_subparsers(help='', dest='net_command')
    forward_parser = net_parser_subparsers.add_parser('forward',
                                                      help='Forwards ports of a host machine to the container')
    forward_parser.add_argument('-cip', '--container_ip', required='True', help='Container ip')
    forward_parser.add_argument('-cp', '--container_port', required='True', help='Container port')
    forward_parser.add_argument('-hp', '--host_port', required='True', help='Host port')
    forward_parser.add_argument('-hi', '--host_interface', help='Host interface, default is eth0')

    patch_parser = net_parser_subparsers.add_parser('patch')
    patch_parser.add_argument('-n', '--name', required='True', help='Name of the container to be patched')
    patch_parser.add_argument('-sip', '--static-ip', required='True', help='Static ip in the form a.b.c.d/e, like'
                                                                           '10.0.3.100/24')

    args = parser.parse_args()
    logging.info('Received args: {0}'.format(args))
    if args.command == 'copy':
        copy_call(args.original_name, args.new_name)
    if args.command == 'net':
        if args.net_command == 'forward':
            if args.host_interface:
                forward_port(args.container_ip, args.container_port, args.host_port, args.host_interface)
            else:
                forward_port(args.container_ip, args.container_port, args.host_port)

        if args.net_command == 'patch':
            patch_container_config(args.name, args.static_ip)


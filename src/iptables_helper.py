__author__ = 'nikita_kartashov'

from subprocess import call, DEVNULL
import logging


class IptablesHelper(object):
    NAT_RULE_TEMPLATE = 'sudo iptables -t nat '
    FLUSH = '-F'
    LIST = '-L'

    FORWARD_PORT_RULE_TEMPLATE = \
        NAT_RULE_TEMPLATE + '{4} PREROUTING -i {0} -p tcp --dport {1} -j DNAT --to {2}:{3} -s {5}'
    FORWARD_RULE_TEMPLATE = NAT_RULE_TEMPLATE + '{2} PREROUTING -i {0} -j DNAT --to {1} -s {3}'
    ADD = '-A'
    DELETE = '-D'
    CHECK = '-C'

    @staticmethod
    def full_forward(to_ip, host_interface, src, check=True):
        add_command = IptablesHelper.FORWARD_RULE_TEMPLATE.format(host_interface, to_ip, IptablesHelper.ADD, src)
        if check and not IptablesHelper.check_if_forward_rule_exists(to_ip, host_interface, src):
            call(add_command, shell=True)
            logging.info('Added rule: ' + add_command)
        else:
            logging.info('No rule was added due to checking enabled')

    @staticmethod
    def full_unforward(to_ip, host_interface, src):
        delete_command = IptablesHelper.FORWARD_RULE_TEMPLATE.format(host_interface, to_ip, IptablesHelper.DELETE, src)
        call(delete_command, shell=True)
        logging.info('Removed rule: ' + delete_command)

    @staticmethod
    def forward_port(to_ip, to_port, host_port, host_interface, src, check=True):
        add_command = IptablesHelper.FORWARD_PORT_RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port,
                                                                       IptablesHelper.ADD,
                                                                       src)
        if check and not IptablesHelper.check_if_port_forward_rule_exists(to_ip, to_port, host_port, host_interface,
                                                                          src) or not check:
            call(add_command, shell=True)
            logging.info('Added rule: ' + add_command)
        else:
            logging.info('No rule was added due to checking enabled')

    @staticmethod
    def unforward_port(to_ip, to_port, host_port, host_interface, src):
        delete_command = IptablesHelper.FORWARD_PORT_RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port,
                                                                          IptablesHelper.DELETE, src)
        call(delete_command, shell=True)
        logging.info('Removed rule: ' + delete_command)

    @staticmethod
    def check_if_port_forward_rule_exists(to_ip, to_port, host_port, host_interface, src):
        check_command = IptablesHelper.FORWARD_PORT_RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port,
                                                                         IptablesHelper.CHECK,
                                                                         src)
        return call(check_command, stdout=DEVNULL, stderr=DEVNULL, shell=True) == 0

    @staticmethod
    def check_if_forward_rule_exists(to_ip, host_interface, src):
        check_command = IptablesHelper.FORWARD_RULE_TEMPLATE.format(host_interface, to_ip, IptablesHelper.CHECK, src)
        return call(check_command, stdout=DEVNULL, stderr=DEVNULL, shell=True) == 0

    @staticmethod
    def flush():
        flush_command = IptablesHelper.NAT_RULE_TEMPLATE + IptablesHelper.FLUSH
        return call(flush_command, shell=True) == 0

    @staticmethod
    def list():
        list_command = IptablesHelper.NAT_RULE_TEMPLATE + IptablesHelper.LIST
        return call(list_command, shell=True) == 0
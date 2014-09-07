__author__ = 'nikita_kartashov'

import logging

from utils.utils import logged_console_call


class IptablesHelper(object):

    """
    Helper unifying methods working with iptables
    """

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
        """
        Makes a rule, forwarding all packets from *host_interface* to *to_ip*
        :parameter to_ip: ip to which packets will be forwarded
        :parameter host_interface: interface receiving packets
        :parameter src: packet source ip
        :parameter check: whether to check for existence of the rule before making one
        :return: None
        """

        add_command = IptablesHelper.FORWARD_RULE_TEMPLATE.format(host_interface, to_ip, IptablesHelper.ADD, src)
        if check and not IptablesHelper.__check_if_forward_rule_exists(to_ip, host_interface, src):
            logged_console_call(add_command)
        else:
            logging.info('No rule was added due to checking enabled')

    @staticmethod
    def full_unforward(to_ip, host_interface, src):
        """
        Removes the rule made by full_forward command
        :param to_ip: ip to which packets have been forwarded
        :param host_interface: interface receiving packets
        :param src: packet source ip
        :return: None
        """

        delete_command = IptablesHelper.FORWARD_RULE_TEMPLATE.format(host_interface, to_ip, IptablesHelper.DELETE, src)
        logged_console_call(delete_command)

    @staticmethod
    def forward_port(to_ip, to_port, host_port, host_interface, src, check=True):
        """
        Makes a rule, forwarding a packets from a single *host_port* to a single *to_port* of the receiver with *to_ip*
        :param to_ip: ip to which the packets are forwarded
        :param to_port: port to which the packets are forwarded
        :param host_port: ip receiving the packets
        :param host_interface: port receiving the packets
        :param src: packet source ip
        :param check: whether to check for existence of the rule before making one
        :return: None
        """

        add_command = IptablesHelper.FORWARD_PORT_RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port,
                                                                       IptablesHelper.ADD,
                                                                       src)
        if check and not IptablesHelper.__check_if_port_forward_rule_exists(to_ip, to_port, host_port, host_interface,
                                                                          src) or not check:
            logged_console_call(add_command)
        else:
            logging.info('No rule was added due to checking enabled')

    @staticmethod
    def unforward_port(to_ip, to_port, host_port, host_interface, src):
        """
        Removes the rule made by forward_port command
         :param to_ip: ip to which the packets are forwarded
        :param to_port: port to which the packets are forwarded
        :param host_port: ip receiving the packets
        :param host_interface: port receiving the packets
        :param src: packet source ip
        :return: None
        """

        delete_command = IptablesHelper.FORWARD_PORT_RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port,
                                                                          IptablesHelper.DELETE, src)
        logged_console_call(delete_command)

    @staticmethod
    def __check_if_port_forward_rule_exists(to_ip, to_port, host_port, host_interface, src):
        check_command = IptablesHelper.FORWARD_PORT_RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port,
                                                                         IptablesHelper.CHECK,
                                                                         src)
        return logged_console_call(check_command, mute=True) == 0

    @staticmethod
    def __check_if_forward_rule_exists(to_ip, host_interface, src):
        check_command = IptablesHelper.FORWARD_RULE_TEMPLATE.format(host_interface, to_ip, IptablesHelper.CHECK, src)
        return logged_console_call(check_command, mute=True) == 0

    @staticmethod
    def flush():
        """
        Flushes nat table of iptables
        :return: if flushing was successful
        """

        flush_command = IptablesHelper.NAT_RULE_TEMPLATE + IptablesHelper.FLUSH
        return logged_console_call(flush_command) == 0

    @staticmethod
    def list():
        """
        Outputs nat table of iptables
        :return: if listing was successful
        """

        list_command = IptablesHelper.NAT_RULE_TEMPLATE + IptablesHelper.LIST
        return logged_console_call(list_command) == 0
__author__ = 'nikita_kartashov'

from subprocess import call, DEVNULL
import logging


class IptablesHelper(object):
    RULE_TEMPLATE = 'sudo iptables -t nat {4} PREROUTING -i {0} -p tcp --dport {1} -j DNAT --to {2}:{3}'
    ADD = '-A'
    DELETE = '-D'
    CHECK = '-C'

    @staticmethod
    def forward_port(to_ip, to_port, host_port, host_interface, check=True):
        add_cmd = IptablesHelper.RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port, IptablesHelper.ADD)
        if check and not IptablesHelper.check_if_rule_exists(to_ip, to_port, host_port, host_interface) or not check:
            call(add_cmd, shell=True)
            logging.info('Added rule: ' + add_cmd)
        else:
            logging.info('No rule was added due to checking enabled')

    @staticmethod
    def unforward_port(to_ip, to_port, host_port, host_interface):
        delete_cmd = IptablesHelper.RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port, IptablesHelper.DELETE)
        call(delete_cmd, shell=True)
        logging.info('Removed rule: ' + delete_cmd)

    @staticmethod
    def check_if_rule_exists(to_ip, to_port, host_port, host_interface):
        check_cmd = IptablesHelper.RULE_TEMPLATE.format(host_interface, host_port, to_ip, to_port, IptablesHelper.CHECK)
        return call(check_cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True) == 0


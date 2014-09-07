__author__ = 'nikita_kartashov'

from logging import info
from subprocess import call, DEVNULL


def logged_console_call(command, mute=False):
    """
    Logs the *command* and then executes it in a subprocess
    :param command: command in question
    :param mute: if the output is to be discarded
    :return: result of the call
    """

    info(command)
    if mute:
        return call(command, stdout=DEVNULL, stderr=DEVNULL, shell=True)
    else:
        return call(command, shell=True)
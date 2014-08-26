__author__ = 'nikita_kartashov'

from logging import info
from subprocess import call, DEVNULL


def logged_console_call(command, mute=False):
    info(command)
    if mute:
        return call(command, stdout=DEVNULL, stderr=DEVNULL, shell=True)
    else:
        return call(command, shell=True)
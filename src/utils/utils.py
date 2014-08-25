__author__ = 'nikita_kartashov'

from logging import info
from subprocess import call


def logged_console_call(command):
    info(command)
    return call(command, shell=True)
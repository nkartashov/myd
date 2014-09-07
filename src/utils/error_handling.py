__author__ = 'nikita_kartashov'

import logging


def log_print_error(message):
    """
    Prints the error to the screen and logs it
    :param message: error message
    :return: None
    """

    print(message)
    logging.error(message)


def no_config_found_message(container_name, config_path, unprivileged=False):
    """
    Produces the message for a not found container config
    :param container_name: name of the container in question
    :param config_path: path to the config
    :param unprivileged: if the container is unprivileged
    :return: error message
    """

    return 'No config for {2} container {0} at {1}'.format(container_name, config_path,
                                                           'unprivileged' if unprivileged else 'privileged')
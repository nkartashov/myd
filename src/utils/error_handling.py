__author__ = 'nikita_kartashov'

import logging


def log_print_error(message):
    print(message)
    logging.error(message)


def no_config_found_message(container_name, config_path, unprivileged=False):
    return 'No config for {2} container {0} at {1}'.format(container_name, config_path,
                                                           'unprivileged' if unprivileged else 'privileged')
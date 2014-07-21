__author__ = 'nikita_kartashov'

import logging
from pickle import load, dump
from os import path
from uuid import UUID

from .structures.component import Component
from .structures.branch import Branch
from .machines.source_machine import SourceMachine


class Hierarchy(object):
    def __init__(self, path):
        self.__store_path = path
        self.__hierarchy_tree = None
        self.__deserialize()

    def __deserialize(self):
        if path.isfile(self.__store_path):
            with open(self.__store_path) as input_file:
                self.__hierarchy_tree = load(input_file)
            logging.info('Deserialized hierarchy')

    def __serialize(self):
        if self.__hierarchy_tree:
            with open(self.__store_path) as output_file:
                dump(self.__hierarchy_tree, output_file)
            logging.info('Serialized hierarchy')

    def source_machine(self):
        return self.__hierarchy_tree['source_machine'] if self.__hierarchy_tree else None

    def branches(self):
        return self.__hierarchy_tree['branches'] if self.__hierarchy_tree else None

    def new_source_machine(self, name):
        if self.__hierarchy_tree:
            logging.error('Hierarchy already contains a source machine')
            return
        self.__hierarchy_tree = {'source_machine': SourceMachine(name), 'branches': {}}
        logging.info('Added a source machine {0}'.format(name))

    def add_component(self, relative_path):
        if not self.__hierarchy_tree:
            logging.error('Hierarchy does not contain a source machine')
            return
        new_component = Component(relative_path)
        self.source_machine().add_component(new_component)

    def new_branch(self, uuid):
        if not self.__hierarchy_tree:
            logging.error('Hierarchy does not contain a source machine')
            return
        if self.branches().get(uuid, None):
            logging.error('Branch on {0} already exists'.format(uuid))
            return
        if not uuid in self.source_machine():
            logging.error('There is no component {0} in source machine'.format(uuid))
            return
        # TODO: fix branch constructor
        self.branches()[uuid] = Branch()

    def print_hierarchy(self):
        pass
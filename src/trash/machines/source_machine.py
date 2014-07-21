__author__ = 'nikita_kartashov'

import logging
from uuid import UUID

from .src.trash.machines.machine import Machine
from ..src.trash.structures.component import Component
from ..src.trash.utils.decorators import accepts


class SourceMachine(Machine):
    def __init__(self, name):
        super().__init__(name)
        self.__components = {}

    @accepts(object, Component)
    def add_component(self, component):
        intersection = Component.intersection(component, *self.__components.values())
        if intersection:
            logging.error('Cannot add a component, for it clashes with already added ones: '
                          'common prefix {0}'.format(intersection))
            return

        self.__components[UUID()] = component
        logging.info('Added a component {0}'.format(component.relative_path))

    def __contains__(self, uuid):
        return self.__components and uuid in self.__components.keys()

    def list_components(self):
        if not self.__components:
            print('There are no components')
            return
        for uuid, c in self.__components.items():
            print('({0}) {1}'.format(uuid, c.relative_path))
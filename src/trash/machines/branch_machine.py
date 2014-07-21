__author__ = 'nikita_kartashov'

from .src.trash.machines.machine import Machine


class BranchMachine(Machine):
    def __init__(self, source_machine):
        super().__init__()
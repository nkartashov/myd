__author__ = 'nikita_kartashov'

from utils.func_tools import fst, snd


class LxcConfig(object):
    def __init__(self, filename):
        self.__properties = {}
        self.__filename = filename
        self.__has_been_modified = False
        self.__parse(filename)

    def __parse(self, filename):
        with open(filename) as config_file:
            for line in config_file.readlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                value_pair = LxcConfig.__process_line(line)
                self.__append_property_value(*value_pair)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__has_been_modified:
            self.__dump()

    @staticmethod
    def __process_line(line):
        return [item.strip() for item in line.split('=')]

    def __append_property_value(self, key, value):
        existing_values = self.__properties.get(key, [])
        existing_values.append(value)
        self.__properties[key] = existing_values

    def __modified(self):
        self.__has_been_modified = True

    def append_value(self, key, value):
        self.__modified()
        self.__append_property_value(key, value)

    def __getitem__(self, item):
        return self.__properties.get(item, [])

    def erase_property(self, key):
        self.__modified()
        self.__properties[key] = []

    def set_value(self, key, value):
        self.__modified()
        self.__properties[key] = [value]

    def print(self):
        for key, value in self.__properties.items():
                for item in value:
                    print('{0} = {1}'.format(key, item))

    def __dump(self):
        with open(self.__filename, 'w') as config_file:
            for key, value in self.__properties.items():
                for item in value:
                    config_file.write('{0} = {1}\n'.format(key, item))

__author__ = 'nikita_kartashov'

from collections import OrderedDict


class LxcConfig(object):
    """
    Class unifying interaction with container config
    """

    def __init__(self, filename):
        """
        Reads a new config from a filename
        :param filename: filename of the config file
        :return: None
        """

        self.__properties = OrderedDict()
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
        """
        Is called on entering a with statement, does nothing now
        :return: self instance
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Dumps the config if it has been modified
        :param exc_type: UNUSED
        :param exc_val: UNUSED
        :param exc_tb: UNUSED
        :return: None
        """

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
        """
        Appends value to a property
        :param key: property name
        :param value: value to be appended
        :return: None
        """

        self.__modified()
        self.__append_property_value(key, value)

    def __getitem__(self, item):
        return self.__properties.get(item, [])

    def erase_property(self, key):
        """
        Erases all values of the property
        :param key: property name
        :return: None
        """

        self.__modified()
        self.__properties[key] = []

    def remove_last_value(self, key):
        """
        If there is at least 1 value of the property, the last one is removed
        :param key: property name
        :return: None
        """

        if len(self.__properties[key]) > 0:
            self.__modified()
            self.__properties[key].pop()

    def set_value(self, key, value):
        """
        Sets the property to a value
        :param key: property name
        :param value: new value
        :return: None
        """

        self.__modified()
        self.__properties[key] = [value]

    def print(self):
        """
        Prints the config to the screen
        :return: None
        """

        for key, value in self.__properties.items():
                for item in value:
                    print('{0} = {1}'.format(key, item))

    def __dump(self):
        with open(self.__filename, 'w') as config_file:
            for key, value in self.__properties.items():
                for item in value:
                    config_file.write('{0} = {1}\n'.format(key, item))

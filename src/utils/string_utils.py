__author__ = 'nikita_kartashov'


def split_to_function(input_string, split_string, f, strip_string=None):
    """
    Splits the strings, then strips every component, then calls a function on them
    :param input_string: the string to be processed
    :param split_string: characters to split on
    :param f: function to be applied
    :param strip_string: characters to strip
    :return: resulting map object after the performed operations
    """

    def inner_split(s):
        """
        Splits the string on *split_string* characters
        :param s: the string to be split
        :return: list of split parts
        """

        return s.split(split_string)

    def inner_strip(s):
        """
        Strips the string from *strip_string* characters
        :param s: the string to be strip
        :return: stripped string
        """

        if strip_string:
            return s.strip(strip_string)
        return s.strip()

    def inner_map_function(s):
        """
        First applies stripping function then the function provided
        :param s: the string the processed
        :return: the result of the applied function
        """

        return f(inner_strip(s))

    return map(inner_map_function, inner_split(input_string))
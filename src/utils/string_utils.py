__author__ = 'nikita_kartashov'


def split_to_function(input_string, split_string, f, strip_string=None):
    """Three phases: split, strip and map"""

    def inner_split(s):
        return s.split(split_string)

    def inner_strip(s):
        if strip_string:
            return s.strip(strip_string)
        return s.strip()

    def inner_map_function(s):
        return f(inner_strip(s))

    return map(inner_map_function, inner_split(input_string))
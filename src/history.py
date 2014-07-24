__author__ = 'nikita_kartashov'

from utils.func_tools import fst, snd
from functools import reduce


class History(object):

    def __init__(self, history=None):
        self.__history = history if history else []

    def __str__(self):
        return '\n'.join(map(History.node_repr, self.__history))

    def __bool__(self):
        return bool(self.__history)

    @staticmethod
    def new_node(name):
        return name, []

    @staticmethod
    def name(node):
        return fst(node)

    @staticmethod
    def children(node):
        return snd(node)

    @staticmethod
    def children_names(node):
        return map(History.name, History.children(node))

    @staticmethod
    def try_add_child(node, parent, child):
        if History.name(node) == parent:
            History.children(node).append(History.new_node(child))
            return True
        return any(History.try_add_child(child_node, parent, child) for child_node in History.children(node))

    @staticmethod
    def remove_from_node(node, child_to_remove):
        children_names = list(History.children_names(node))
        try:
            child_to_remove_index = children_names.index(child_to_remove)
            result = History.children(History.children(node)[child_to_remove_index]), True
            del History.children(node)[child_to_remove_index]
            return result
        except ValueError:
            children_call_result = [History.remove_from_node(child_node, child_to_remove)
                                    for child_node in History.children(node)]
            return reduce(lambda l, r: l if snd(l) else r,
                          children_call_result, ([], False))

    @staticmethod
    def node_repr(node):
        result = History.name(node)
        if History.children(node):
            result += ':[' + ', '.join(map(History.node_repr, History.children(node))) + ']'
        return result

    def remember_copy(self, original_name, new_name):
        if not any(History.try_add_child(branch, original_name, new_name) for branch in self.__history):
            new_branch = History.new_node(original_name)
            History.try_add_child(new_branch, original_name, new_name)
            self.__history.append(new_branch)

    def remember_remove(self, name):
        for branch in self.__history:
            if History.name(branch) == name:
                self.__history.extend(History.children(branch))
                self.__history.remove(branch)
                break
            resulting_orphans, remove_occured = History.remove_from_node(branch, name)
            if remove_occured:
                self.__history.extend(resulting_orphans)
                break


if __name__ == '__main__':
    h = History()
    h.remember_copy('lol', 'foz')
    h.remember_copy('lol', 'qux')
    h.remember_copy('foz', 'baz')
    h.remember_copy('foz', 'typhos')
    h.remember_copy('a', 'b')
    print(h)
    h.remember_remove('lol')
    print(h)
    # h.remember_remove('foz')
    # print(h)





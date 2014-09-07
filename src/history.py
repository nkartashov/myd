__author__ = 'nikita_kartashov'

from utils.func_tools import fst, snd
from functools import reduce


class History(object):
    """
    Object handling the history of container creation, copying and removal
    """

    def __init__(self, history=None):
        """
        Makes an object from existing history or creates one anew
        :param history:
        :return: None
        """

        self.__history = history if history else []

    def __str__(self):
        """
        Builds a string representation of history
        :return: string with history representation
        """

        return '\n'.join(map(History.node_repr, self.__history))

    def __bool__(self):
        """
        Returns whether history is present
        :return: if history is present
        """

        return bool(self.__history)

    @staticmethod
    def new_node(name):
        """
        Makes a new history node with *name*
        :param name: name of the new node
        :return: new node as a tuple
        """

        return name, []

    @staticmethod
    def name(node):
        """
        Gets the name of the *node*
        :param node: node in question
        :return: name of the node
        """

        return fst(node)

    @staticmethod
    def children(node):
        """
        Gets list of *node*'s children
        :param node: node in question
        :return: list of children
        """

        return snd(node)

    @staticmethod
    def children_names(node):
        """
        Gets the names of the *node*'s children
        :param node: node in question
        :return: map object of children's names
        """

        return map(History.name, History.children(node))

    @staticmethod
    def try_add_child(node, parent, child):
        """
        Tries to add the *child* to the *node*
        :param node: node in question
        :param parent: name of the child's parent
        :param child: child to add
        :return: if the addition was successful
        """

        if History.name(node) == parent:
            History.children(node).append(History.new_node(child))
            return True
        return any(History.try_add_child(child_node, parent, child) for child_node in History.children(node))

    @staticmethod
    def remove_from_node(node, child_to_remove):
        """
        Removes the *child_to_remove* from a *node*
        :param node: node in question
        :param child_to_remove: child in question
        :return: tuple with orphans and whether remove occurred
        """

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
        """
        Returns the string representation of a node
        :param node: node in question
        :return: string representation of the node
        """

        result = History.name(node)
        if History.children(node):
            result += ':[' + ', '.join(map(History.node_repr, History.children(node))) + ']'
        return result

    def remember_copy(self, original_name, new_name):
        """
        Puts the information about the copying of *original_name* container into *new_name* one
        :param original_name: name of the container to copy
        :param new_name: name of the resulting container
        :return: None
        """

        if not any(History.try_add_child(branch, original_name, new_name) for branch in self.__history):
            new_branch = History.new_node(original_name)
            History.try_add_child(new_branch, original_name, new_name)
            self.__history.append(new_branch)

    def remember_remove(self, name):
        """
        Puts the information about the removal of *name* container
        :param name: name of the container to remove
        :return: None
        """

        for branch in self.__history:
            if History.name(branch) == name:
                self.__history.extend(History.children(branch))
                self.__history.remove(branch)
                break
            resulting_orphans, remove_occurred = History.remove_from_node(branch, name)
            if remove_occurred:
                self.__history.extend(resulting_orphans)
                break

    def remember_create(self, name):
        """
        Puts the information about the creation of *name* container
        :param name: name of the created container
        :return: None
        """

        self.__history.append(History.new_node(name))


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





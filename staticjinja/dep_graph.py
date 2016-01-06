# -*- coding:utf-8 -*-

"""
Dependency graph for staticjina
"""

from copy import deepcopy


class DepGraph(object):
    """
    A directed graph which will handle dependencies between templates and data
    files in a site.

    :param site:
        A :class:`Site <Site>` object.

    """
    def __init__(self, site):
        self.parents = dict(
                (s, set()) for s in site.jinja_names + site.data_names
                )
        self.children = deepcopy(self.parents)

        for filename in site.jinja_names:
            self.parents[filename] = site.get_file_dep(filename)
            for d in self.parents[filename]:
                self.children[d].add(filename)

        self.site = site

    def connected_components(self, adjacency, start):
        """Returns the (directed) connected component of start in the graph with
        given adjacency dict.

        Uses a classical depth first search.

        :param adjacency: the adjacency dict to be used (will be either
        self.children or self.parents in all foreseen uses)

        :param start: the vertex in the graph whose connected component we
        seek.
        """

        seen = set([start])
        stack = [iter(adjacency[start])]
        while stack:
            children = stack[-1]
            try:
                child = next(children)
                if child not in seen:
                    yield child
                seen.add(child)
                stack.append(iter(adjacency[child]))
            except StopIteration:
                stack.pop()

    def get_descendants(self, filename):
        """Returns all descendant of the given template or data file.

        :param filename: the template or data file whose descendant we seek.
        """
        return self.connected_components(self.children, filename)

    def update(self, filename):
        """
        Updates the part of this dependency graph directly linked to some
        template or data file.

        :param filename: A string giving the relative path of the template or
        data file.
        """
        old_parents = self.parents.get(filename, set())
        new_parents = self.site.get_file_dep(filename)
        if new_parents != old_parents:
            for lost_parent in old_parents.difference(new_parents):
                self.children[lost_parent].remove(filename)
            for new_parent in new_parents.difference(old_parents):
                self.children[new_parent].add(filename)
            self.parents[filename] = new_parents

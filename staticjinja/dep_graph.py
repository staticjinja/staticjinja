# -*- coding:utf-8 -*-

"""
Dependency graph for staticjinja
"""


class DepGraph(object):
    """
    A directed graph which will handle dependencies between sources in a site.

    :param parents:
        A dictionary whose keys are vertices of the graph and each value is the
        set of child vertices of the key vertex.

    :param children:
        A dictionary whose keys are vertices of the graph and each value is the
        set of parents vertices of the key vertex.

    """
    def __init__(self, parents, children):
        self.parents = parents
        self.children = children

    @classmethod
    def from_parents(cls, parents):
        """
        Buils a graph from a dictionnary of directed edges
        by building the dictionnary of children edges.

        :param parents:
            A dictionary whose keys are vertices of the graph and each value is
            the set of child vertices of the key vertex.
        """
        children = {}
        for vertex in parents:
            children[vertex] = set()
        for vertex in parents:
            for d in parents[vertex]:
                children[d].add(vertex)
        return cls(parents, children)

    def connected_components(self, direction, start):
        """Returns the (directed) connected component of start in the graph
        (including start).

        Uses a classical depth first search.

        :param direction: either 'descendants' or 'ancestors'

        :param start: the vertex in the graph whose connected component we
            seek.

        """

        if direction == 'descendants':
            adjacency = self.children
        elif direction == 'ancestors':
            adjacency = self.parents
        else:
            raise ValueError(
                    'direction should be either descendants or ancestors'
                    )

        yield start
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

    def get_descendants(self, vertex):
        """Returns all descendants of the given vertex.

        :param vertex: the vertex whose descendant we seek.
        """
        return self.connected_components('descendants', vertex)

    def update_vertex(self, vertex, new_parents):
        """
        Updates the part of this graph directly linked to some vertex.

        :param vertex: A vertex of the graph (it can be a new one)

        :param new_parents: the new set of parents of vertex.

        """
        old_parents = self.parents.get(vertex, set())
        if new_parents != old_parents:
            for lost_parent in old_parents.difference(new_parents):
                self.children[lost_parent].remove(vertex)
            for new_parent in new_parents.difference(old_parents):
                self.children[new_parent].add(vertex)
            self.parents[vertex] = new_parents

    def remove_vertex(self, vertex):
        """Remove a vertex from the graph.

        :param vertex: A vertex of the graph (it can be a new one)

        """
        del self.parents[vertex]
        del self.children[vertex]
        for parents in self.parents.values():
            parents.discard(vertex)
        for children in self.children.values():
            children.discard(vertex)

    def add_vertex(self, vertex, parents):
        """Add a vertex to the graph.

        :param vertex: A new vertex

        :param parents: The parents of the new vertex

        """
        self.parents[vertex] = parents
        self.children[vertex] = set()
        for parent in parents:
            self.children[parent].add(vertex)

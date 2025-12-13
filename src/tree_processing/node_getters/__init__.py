from typing import Any, NamedTuple

from .. import rejected


class NodeError(ValueError):
    '''Represents encountering a node in a traversal which should abort
    the entire traversal with an error (which can be detected to
    trigger any necessary cleanup).'''
    pass


class Node(NamedTuple):
    '''Structure representing a node in a traversal.'''
    internal: bool # whether the node may potentially have children.
    name: Any # a relationship between the parent and current nodes.
    current: Any # The current node in the traversal.
    parent: Any # The parent of the current node in the traversal.
    # N.B. For "mirroring" operations, `current` and `parent` could be
    # (src, dst) tuples rather than single values.


def _gen(raw_get, make_node, parent):
    nodes = (make_node(parent, child) for child in raw_get(parent))
    return (node for node in nodes if node is not rejected)


def make_getter(raw_get, make_node):
    return lambda parent: _gen(raw_get, make_node, parent)

from pathlib import Path

from .actions import Node
from .filesystem import get_children


def topdown(root, get_children):
    stack = [root]
    while stack:
        top = stack.pop()
        children = get_children(top)
        leaves = [c for c in children if not c.internal]
        branches = [c for c in children if c.internal]
        yield branches, leaves
        stack += branches


def topdown_test():
    return topdown(Node(True, None, '.', None), get_children)

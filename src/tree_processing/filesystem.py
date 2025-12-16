from .traversal import topdown as _topdown
from .node_getters import make_getter as _make_getter
from .node_getters.filesystem import default_get, make_node, make_root, raw_get
from .actions.filesystem import *


def topdown(
    raw_src='.', raw_dst=None, *,
    get=None, raw_get=raw_get, make_node=make_node, sort_key=None
):
    if get is None:
        get = _make_getter(raw_get, make_node)
    return _topdown(make_root(raw_src, raw_dst), get, sort_key=sort_key)

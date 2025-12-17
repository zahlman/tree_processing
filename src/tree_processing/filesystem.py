from functools import partial

from . import traversal
from .node_getters import make_getter as _make_getter
from .node_getters.filesystem import default_get, make_node, make_root, raw_get
from .actions.filesystem import *


def _adapter(
    t, raw_src='.', raw_dst=None, *,
    get=None, raw_get=raw_get, make_node=make_node, sort_key=None
):
    get = _make_getter(raw_get, make_node) if get is None else get
    return t(make_root(raw_src, raw_dst), get, sort_key=sort_key)


topdown = partial(_adapter, traversal.topdown)
top_down = partial(_adapter, traversal.top_down)
topdown_depth_first = partial(_adapter, traversal.topdown_depth_first)
top_down_depth_first = partial(_adapter, traversal.top_down_depth_first)
topdown_breadth_first = partial(_adapter, traversal.topdown_breadth_first)
top_down_breadth_first = partial(_adapter, traversal.topdown_breadth_first)

from functools import partial, wraps
from operator import add


class NodeError(ValueError):
    '''Represents encountering a node in a traversal which should abort
    the entire traversal with an error (which can be detected to
    trigger any necessary cleanup).'''
    pass


class rejected:
    """A special value used to indicate that a node was "rejected"
    during the processing of a tree.

    An "action" callable can return this to indicate that a leaf node didn't
    produce a value that should be accumulated; for a top-down traversal,
    returning this for an internal node causes its children to be pruned.

    This is therefore not a valid result for accumulation; as an
    implementation detail, the accumulator is initialized with this value to
    signal that actions won't expect an accumulator argument.

    Likewise, a Node-creation function can return this value to skip creating
    a Node from a given raw-get result. (The raw-getter should not normally
    yield this value; the Node-creator will have to handle it if it does.)
    """
    # The object is intended to be singleton, so the name is re-bound so as to
    # avoid exposing a name for the class. This can't protect against
    # deliberate hacks like `tree_processing.rejected = ...` or
    # `rejected_copy = rejected.__class__()`, and doesn't try.
    # However, avoiding mutation of the singleton instance seems worthwhile,
    # and possibly saves a few bytes of memory.
    __slots__ = ()
rejected = rejected()


def _normalize_act(act):
    try:
        process_folder, process_file = act
    except TypeError: # not iterable, so a single callable
        return act
    except ValueError: # a single callable, or else propagate the error
        act, = act
        return act
    else: # create a simple dispatch for the two callables.
        return lambda n: (process_folder if n.internal else process_file)(n)


def _process(traversal, act):
    node, act = next(traversal), _normalize_act(act)
    while True:
        result = act(node)
        try:
            node = traversal.send(result)
        except StopIteration:
            return result


def process(traverse, root, get_children, act):
    return _process(iter(traverse(root, get_children)), act)


class Traversal:
    def __init__(self, traverse, root, get_children):
        self._traverse, self._root, self._get = traverse, root, get_children


    def __iter__(self):
        yield from self._traverse(self._root, self._get)


    def __call__(self, *act):
        return _process(iter(self), act)


def traversal(func):
    """Converts traversal generators into `Traversal` constructors."""
    return wraps(func)(partial(Traversal, func))


def accumulator(initial, accumulate):
    """Decorator for accumulating results from actions (or action-pairs).

    An internal accumulator is initialized at the start of the traversal,
    and updated each time the action is applied to a node. (Note: if this is
    done by modifying the accumulator's state, the `accumulate` function must
    explicitly `return` the same object.) The update is skipped whenever the
    action's result is `rejected`.

    initial -> the initial state of the accumulator. Cannot be `rejected`.
    accumulate(current, result) -> a function which updates the accumulator.
        Given the `current` value of the accumulator and the `result` of
        acting on the current node, returns an updated result (may or may
        not be the same object as before). May not return `rejected`.

    This can be used to decorate any callable used as an action (applied to
    all nodes), or called with a pair of functions (applied to internal and
    leaf nodes respectively).
    """
    if initial is rejected:
        raise ValueError("cannot initialize accumulator with `rejected`")
    def _wrapper(*args):
        act = _normalize_act(args)
        @wraps(act)
        def _wrapped(node):
            nonlocal initial
            result = act(node)
            if result is rejected:
                return rejected
            initial = accumulate(initial, result)
            if initial is rejected:
                raise NodeError("accumulator returned `rejected`")
            return initial
        return _wrapped
    return _wrapper


# The most common case of accumulation.
sum_results = accumulator(0, add)
sum_results.__qualname__ = sum_results.__name__ = 'sum_results'
sum_results.__doc__ = """\
Sums the results of actions applied at each node.

Equivalent to using `accumulator(0, add)`.

args -> a single action applied to all nodes, or a pair of actions where
        the first is applied to internal nodes and the second to leaves.
"""

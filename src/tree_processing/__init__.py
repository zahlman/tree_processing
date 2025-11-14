from functools import partial, wraps


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


def _process_one(node, traversal, act, accumulator):
    use_accumulator = (accumulator[0] is not rejected)
    result = act(node, accumulator[0]) if use_accumulator else act(node)
    if result is not rejected and use_accumulator:
        accumulator[0] = result
    return traversal.send(result)


def _dispatch(process_folder, process_file):
    def _act(node, *args):
        return (process_folder if node.internal else process_file)(node, *args)
    return _act


def _normalize_act(act):
    try:
        process_folder, process_file = act
    except TypeError: # not iterable, so a single callable
        # If an iterable is provided but it has the wrong number of
        # callables, that `ValueError` should propagate.
        return act
    else:
        return _dispatch(process_folder, process_file)


def _process(traversal, act, accumulator):
    traversal = iter(traversal)
    node, act = next(traversal), _normalize_act(act)
    while True:
        try:
            node = _process_one(node, traversal, act, accumulator)
        except StopIteration:
            return accumulator[0]


def process(traverse, root, get_children, act, initial=rejected):
    return _process(traverse(root, get_children), act, [initial])


class Traversal:
    def __init__(self, traverse, root, get_children):
        self._traverse, self._root, self._get = traverse, root, get_children


    def __iter__(self):
        yield from self._traverse(self._root, self._get)


    def __call__(self, act, initial=rejected):
        return _process(iter(self), act, [initial])


def traversal(func):
    """Converts traversal generators into `Traversal` constructors."""
    return wraps(func)(partial(Traversal, func))


def accumulator(initial, accumulate):
    """Converts non-accumulating actions (or action-pairs) to accumulate.

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
            return result
        return _wrapped
    return _wrapper

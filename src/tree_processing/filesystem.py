from shutil import copy
from .actions import chainable, filterable, Node


# Some useful actions and filters specifically for filesystem traversals.


@chainable
def not_hidden(node: Node):
    return not node.name.startswith('.')


@chainable
def src_is_regular_file(node: Node):
    src, dst = node.current
    return src.is_file()


@filterable
def recurse_into_folders(node: Node):
    '''A helper to do nothing special with folders.'''
    pass


# Adapt a function that accepts src and dst paths,
# into one that expects a `(src, dst)` pair in `node.current`.
def _mirror(func):
    return filterable(lambda node: func(*node.current))


#hardlink_or_copy_files = _reflect_regular_file(hardlink_or_copy)
copy_files = _mirror(filterable(copy).which(src_is_regular_file))


def _fake_copy(src, dst): # For testing.
    print(f'Would copy {src} to {dst}')


fake_copy_files = _mirror(filterable(_fake_copy).which(src_is_regular_file))


@filterable
def propagate_folders(node: Node):
    src, dst = node.current
    assert src.is_dir()
    dst.mkdir(exist_ok=True)


@filterable
def fake_propagate_folders(node: Node):
    src, dst = node.current
    assert src.is_dir()
    print(f'Would create folder {dst} if missing')

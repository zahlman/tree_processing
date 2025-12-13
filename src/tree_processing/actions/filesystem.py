from os import link
from shutil import copy
from . import chainable, filterable
from ..node_getters import Node


@chainable
def not_hidden(node: Node):
    '''A helper to filter out "hidden" files and folders on UNIX-like systems
    (i.e. those whose names start with a dot).'''
    return not node.name.startswith('.')


@chainable
def src_is_regular_file(node: Node):
    '''A helper to filter out symlinks and other non-regular files.'''
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


# Path.hardlink_to requires 3.10.
# For better compatibility, we fall back to the os module
# and also fall back on copying if hardlinks fail for any reason.
def hardlink_or_copy(src, dst):
    '''A helper to hard-link from the source to the destination when possible,
    and copy otherwise.'''
    try:
        link(src, dst)
    except:
        copy(src, dst)
hardlink_or_copy_files = _mirror(hardlink_or_copy)


copy_files = _mirror(copy)


@filterable
def propagate_folders(node: Node):
    '''A helper to create folders in the destination file tree
    which correspond to the source file tree.'''
    src, dst = node.current
    assert src.is_dir()
    dst.mkdir(exist_ok=True)

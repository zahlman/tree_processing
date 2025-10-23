from tree_processing.actions.filesystem import fake_propagate_folders, fake_copy_regular_files, not_hidden
from tree_processing.node_getters.filesystem import default_get, make_root
from tree_processing.traversal import topdown
from tree_processing.actions import Node
from tree_processing import process


def test_fake_copy():
    root = make_root('src', '/tmp')
    not_pycache = lambda node: node.name != '__pycache__'
    process_folder = fake_propagate_folders.which(not_hidden & not_pycache)
    process_file = fake_copy_regular_files.which(not_hidden)
    process(topdown, root, default_get, (process_folder, process_file))
    assert False # just see the printed output for now.


def test_naive_iterate():
    root = make_root('src', '/tmp')
    for node in topdown(root, default_get):
        src, dst = node.current
        if not src.name.endswith('.pyc'): # still checks __pycache__ folders!
            print(f"mirror {src} -> {dst}")
    assert False


def incremented_folders(f, counter):
    folders, files = counter
    return (folders + 1, files)


def incremented_files(f, counter):
    folders, files = counter
    return (folders, files + 1)


def test_count_immutable():
    root = make_root('src')
    act = (incremented_folders, incremented_files)
    assert not process(topdown, make_root('src'), default_get, act, (0, 0))


def increment_folders(f, counter):
    counter[0] += 1
    return counter


def increment_files(f, counter):
    counter[1] += 1
    return counter


def test_count_mutable():
    root = make_root('src')
    act = (increment_folders, increment_files)
    assert not process(topdown, make_root('src'), default_get, act, [0, 0])

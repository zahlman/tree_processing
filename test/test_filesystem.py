from pathlib import Path

from tree_processing.filesystem import fake_propagate_folders, fake_copy_files, get_children, not_hidden
from tree_processing.traversal import topdown
from tree_processing.actions import _rejected, Node

def test_fake_copy():
    root = Node(True, None, (Path('.'), Path('/tmp')), None)
    recurse_branches = []
    traversal = topdown(root, get_children)
    node = next(traversal)
    process_folder = fake_propagate_folders.which(not_hidden)
    process_file = fake_copy_files.which(not_hidden)
    while True:
        try:
            if node.internal:
                result = process_folder(node) is not _rejected
            else:
                result = process_file(node)
            node = traversal.send(result)
        except StopIteration:
            break
    assert False # for now, to see output

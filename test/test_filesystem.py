from pathlib import Path

from tree_processing.actions.filesystem import fake_propagate_folders, fake_copy_regular_files, not_hidden
from tree_processing.node_getters.filesystem import default_get
from tree_processing.traversal import topdown
from tree_processing.actions import Node
from tree_processing import process


def test_fake_copy():
    root = Node(True, None, (Path('.'), Path('/tmp')), None)
    not_pycache = lambda node: node.name != '__pycache__'
    process_folder = fake_propagate_folders.which(not_hidden & not_pycache)
    process_file = fake_copy_regular_files.which(not_hidden)
    # This will fail, but lets us see output for now.
    assert process(topdown, root, default_get, (process_folder, process_file))

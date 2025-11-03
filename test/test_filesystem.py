from tree_processing.actions.filesystem import fake_propagate_folders, fake_copy_regular_files, not_hidden
from tree_processing.node_getters.filesystem import default_get, make_root
from tree_processing.traversal import topdown
from tree_processing.actions import Node
from tree_processing import process

from os import chdir, getcwd, mkdir
from pathlib import Path
from zipfile import ZipFile

from pytest import fixture, mark
parametrize = mark.parametrize


TREE_DIR = Path(__file__).parent / 'trees'


@fixture(params=('empty', 'sample'))
def setup(tmpdir, request):
    old = getcwd()
    # Unzip a sample file hierarchy directly into the tmpdir.
    name = request.param
    with ZipFile(TREE_DIR / f'{name}.zip') as zf:
        zf.extractall(tmpdir)
    chdir(tmpdir)
    yield (TREE_DIR / f'{name}.toml').read_text()
    chdir(old)


def test_fake_copy(tmpdir, setup):
    root = make_root('.', '/tmp')
    process_folder = fake_propagate_folders.which(not_hidden)
    process_file = fake_copy_regular_files.which(not_hidden)
    process(topdown, root, default_get, (process_folder, process_file))
    assert False # just see the printed output for now.


def test_naive_iterate(tmpdir, setup):
    root = make_root('.', '/tmp')
    for node in topdown(root, default_get):
        src, dst = node.current
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

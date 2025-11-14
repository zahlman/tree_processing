from tree_processing.actions.filesystem import fake_propagate_folders, fake_copy_regular_files, not_hidden
from tree_processing.node_getters.filesystem import default_get, make_root
from tree_processing.traversal import topdown
from tree_processing.actions import Node
from tree_processing import process, accumulator

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


def folder_count(f):
    return (1, 0)


def file_count(f):
    return (0, 1)


def pairwise_sum(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])


def test_count_immutable():
    root = make_root('src')
    act = accumulator((0, 0), pairwise_sum)(folder_count, file_count)
    assert not process(topdown, make_root('src'), default_get, act)


def pairwise_add(t1, t2):
    t1[0] += t2[0]
    t1[1] += t2[1]
    return t1


def test_count_mutable():
    root = make_root('src')
    act = accumulator([0, 0], pairwise_add)(folder_count, file_count)
    assert not process(topdown, make_root('src'), default_get, act)

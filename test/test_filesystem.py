from tree_processing.actions.filesystem import fake_propagate_folders, fake_copy_regular_files, not_hidden, copy_files, propagate_folders
from tree_processing.node_getters.filesystem import default_get, make_root
from tree_processing.traversal import topdown
from tree_processing.actions import Node
from tree_processing import process, accumulator

from operator import add
from os import chdir, getcwd, mkdir
from pathlib import Path
try:
    from tomllib import load as load_toml
except ImportError:
    from tomli import load as load_toml
from zipfile import ZipFile

from pytest import fixture, mark
parametrize = mark.parametrize


TREE_DIR = Path(__file__).parent / 'trees'


@fixture(params=('empty', 'sample'))
def expected(tmpdir, request):
    old = getcwd()
    # Unzip a sample file hierarchy directly into the tmpdir.
    name = request.param
    with ZipFile(TREE_DIR / f'{name}.zip') as zf:
        zf.extractall(tmpdir)
    chdir(tmpdir)
    with open(TREE_DIR / f'{name}.toml', 'rb') as f:
        yield load_toml(f)['expected']
    chdir(old)


def test_fake_copy(expected, capsys):
    root = make_root('.', '/tmp')
    process_folder = fake_propagate_folders.which(not_hidden)
    process_file = fake_copy_regular_files.which(not_hidden)
    topdown(root, default_get)(process_folder, process_file)
    assert capsys.readouterr().out == expected['fake_copy']


def test_naive_iterate(expected, capsys):
    root = make_root('.', '/tmp')
    for node in topdown(root, default_get):
        src, dst = node.current
        print(f"mirror {src} -> {dst}")
    assert capsys.readouterr().out == expected['naive_iterate']


def folder_count(f):
    return (1, 0)


def file_count(f):
    return (0, 1)


def pairwise_sum(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])


def test_count_immutable(expected):
    act = accumulator((0, 0), pairwise_sum)(folder_count, file_count)
    result = topdown(make_root('.'), default_get)(act)
    assert isinstance(result, tuple)
    assert result == tuple(expected['count'])


def pairwise_add(t1, t2):
    t1[0] += t2[0]
    t1[1] += t2[1]
    return t1


def test_count_mutable(expected):
    act = accumulator([0, 0], pairwise_add)(folder_count, file_count)
    result = topdown(make_root('.'), default_get)(act)
    assert isinstance(result, list)
    assert result == expected['count']


def test_copy_tree(expected):
    # TODO get a unique name for the dest folder, to make separate
    # copies for each input test case.
    topdown(make_root('.', '../copy'), default_get)(propagate_folders, copy_files)
    # check the destination tree contents.
    # The TOML should have some explicit manifest of them.


def _display_files(node):
    if not node.internal:
        print(f'{node.current}')


# TODO: make `~hidden` work.
# TODO: make `default_get` filterable with `.which`.
def test_print_visible_files(expected):
    # When a single action is passed, it's used for both files and folders.
    topdown(make_root('.'), default_get)(_display_files)
    assert False # inspect output manually for now


# The `accumulator` decorator lets the action accumulate results across nodes.
@accumulator(0, add)
def _add_lines(node):
    if node.internal:
        return 0 # skip folders
    file_path = node.current
    # The built-in traversals provide pathlib.Path objects.
    assert file_path.is_file()
    with open(file_path) as f:
        return sum(1 for _ in f)


def test_count_all_lines(expected):
    print(topdown(make_root('.'), default_get)(_add_lines))
    assert False

# `tree_processing` - Elegant composition of tree-traversal algorithms

[![](https://img.shields.io/pypi/v/tree_processing.svg)](https://pypi.org/project/tree_processing)
<!-- [![Documentation Status](https://readthedocs.org/projects/tree_processing/badge/?version=latest)](https://tree_processing.readthedocs.io/en/latest/?version=latest) -->

## Installation

`pip install tree_processing`

## tl;dr

Stop writing complex logic with `os.walk` like this:

```
results = []
for (path, dirnames, filenames) in os.walk(x):
    # Compare certain files between x and y folder hierarchies.
    for filename in filenames:
        if not valid_filename(filename):
            continue
        x_path = os.path.join(path, filename)
        if filter_path(x_path):
            continue
        y_path = os.path.join(y, os.path.relpath(path, x), filename)
        results.append(compare(x_path, y_path))
    to_recurse = []
    for dirname in dirnames:
        dirpath = os.path.join(path, dirname)
        if valid_foldername(dirname) and not filter_path(dirpath):
            to_recurse.append(dirname)
    dirnames[:] = to_recurse
```

Use `tree_processing`, and write code like this instead:

```
traversal = topdown(x, y, get=folders_and_files.which(~filter_path))
process_folder = recurse_into_folders.which(valid_foldername)
process_file = compare_files.which(valid_filename)
accumulate = accumulator([], append_not_none)
results = traversal(accumulate(process_folder, process_file))
```

And use the same tools to process tree data structures in your code, too.

## How it Works

Conceptually, these tree traversals involve four separate tasks:

* Actually discovering and iterating over nodes of the tree
* Deciding which nodes are relevant to the overall process (filtering)
* Operating on the relevant nodes
* Accumulating results from the operations

But the obvious way to write the code is complex, [because](https://www.youtube.com/watch?v=SxdOUGdseq4) the code for those tasks is [complected](https://en.wiktionary.org/wiki/complect). The goal of `tree_processing` is to let you think about those tasks separately, and combine them in a simple, boilerplate-free way. (It also allows describing the accumulation of results declaratively, rather than explicitly repeatedly modifying an accumulator variable inside a loop.)

First, given an abstract root node and a *getter* (rule for finding the children of a node), a *traversal algorithm* produces a `Traversal` object representing the entire tree. This can be *iterated over* like a generator for lower-level use, but the main use case is to *call* the `Traversal` to process the entire tree. `Traversal` is a class, but the design of `tree_processing` otherwise shuns classes — you can express the missing pieces of logic in the natural way, with ordinary functions.

The per-node *actions* are represented by arbitrary callable objects — you can pass functions directly, or instances of your own classes implementing `__call__`. A `Traversal` is called using either a single callable applied to all nodes, or two callables (one for internal nodes and one for leaf nodes).

Passing an `initial` value for accumulation signals that results should be accumulated. The processing callables will be passed the current accumulated value and are responsible for updating it, which they can do either by mutating the existing value or returning a new one. Helper decorators are provided to combine processing and accumulation logic; this provides flexibility without forcing you to pass a separate argument for the accumulation function.

Filtering is naturally a modification to other parts of the process, rather than a step in itself. But `tree_processing` still simplifies the code greatly, by providing some useful decorators. You can combine decorated "filter" callables into a "chain", and easily apply their logic to filter the tree traversal ahead of time, as well as to "reject" nodes during processing. (In a top-down traversal, if an internal node is rejected, its children will not be visited.)

`tree_processing` offers special support for filesystem operations, in the form of common actions compatible with the traversal system and a standard getter (by default, it does not follow symlinks and treats them as ordinary files). But the same core logic lets you process any kind of tree by just filling in the blanks in the algorithm.

## Examples

Copy all files, folders and symlinks (like `shutil.copytree` with `symlinks=True` and `copy_function=shutil.copy`:

```
from tree_processing.filesystem import copy_files, propagate_folders, topdown

def copy_tree(src, dst):
    topdown(src, dst)(propagate_folders, copy_files)
```

List non-hidden files in non-hidden folders:

```
from tree_processing.filesystem import default_get, hidden, topdown

def display_files(node):
    if not node.internal:
        print(f'{node.current}')

def print_visible_files(src):
    # When a single action is passed, it's used for both files and folders.
    topdown(src, get=default_get.which(~hidden))(display_files)
```

Count lines in all files (assuming only directories and regular files):

```
from tree_processing import sum_results
from tree_processing.filesystem import topdown

def add_lines(node):
    if node.internal:
        return 0 # skip folders
    file_path = node.current
    # The built-in traversals provide pathlib.Path objects.
    assert file_path.is_file()
    with open(file_path) as f:
        return sum(1 for _ in f)

# The `sum_results` decorator adds up results from processing each node.
# It can also be used with ordinary `@decorator` syntax — but because that
# involves calling it ahead of time, the sum would not be reset between
# traversals. Using it this way, the sum starts from 0 each time that
# `count_all_lines` is called.
def count_all_lines(src):
    return topdown(src)(sum_results(add_lines))
```

Using separate file and folder handlers, the product of file name lengths:

```
from operator import mul # to build a custom accumulator

from tree_processing import accumulator
from tree_processing.filesystem import topdown

def file_name_length(node):
    return len(node.name)

def file_name_length_product(src):
    # The decorator can also be applied to a pair of callables:
    process = accumulator(1, mul)(lambda node: 1, file_name_length)
    # (We return 1 for folders to leave the product unchanged.)
    return topdown(src)(process)
```

----

Copyright &copy; 2025 Karl Knechtel

This project is open source software, distributed under the terms of the MIT License.
Please see `LICENSE.txt` for details.

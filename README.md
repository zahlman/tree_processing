# `tree_processing` - Elegant composition of tree-traversal algorithms

[![](https://img.shields.io/pypi/v/tree_processing.svg)](https://pypi.org/project/tree_processing)
<!-- [![Documentation Status](https://readthedocs.org/projects/tree_processing/badge/?version=latest)](https://tree_processing.readthedocs.io/en/latest/?version=latest) -->

## Installation

`pip install tree_processing`

## Description

`tree_processing` is designed to generalize the process of operating on a tree of files and folders - whether that's to rename everything, copy it somewhere else. It's meant to take the annoyance out of walking the directory structure with `pathlib.Path.walk` (or `os.walk`), while still offering more power and flexibility than `shutil`'s tree functions. Simply specify the action to take on files and folders, and `tree_processing` takes care of the rest. Several common actions are also defined for convenience.

The basic algorithm is also designed to be extensible, such that any kind of tree can be walked - treating internal nodes as "directories" and leaf nodes as "files". Unlike classical implementations of the Visitor pattern, however, polymorphic treatment of internal and leaf nodes is left up to the end user (for example, using `functools.singledispatch`).

By default, symlinks are treated as ordinary files. 

## Examples

Copy all files, folders and symlinks (like `shutil.copytree` with `symlinks=True` and `copy_function=shutil.copy`:

```
from tree_processing import PathVisitor, copy_file, copy_folder

def copy_tree(src, dst):
    PathVisitor(copy_folder.to(dst), copy_file.to(dst)).process(src)
```

Count lines in all files (assuming only directories and regular files):

```
from tree_processing import PathVisitor, recurse_into_folders

def line_count(file_path):
    # The built-in traversals provide pathlib.Path objects.
    if not file_path.is_file():
        raise NotImplementedError
    # Iterate over the file and count lines in Python.
    # Alternately, we could e.g. shell out to `wc -l` on Linux/Mac.
    with open(filename) as f:
        return sum(1 for _ in f)

def count_all_lines(src):
    return sum(PathVisitor(recurse_into_folders, line_count).results())
```

List non-hidden files in non-hidden folders (not quite like `ls -1R` - this will show the path to each file, instead of grouping the results by folder):

```
from tree_processing import PathVisitor

def not_hidden(src, item):
    return not item.name.startswith('.')

def visible_files(src):
    files = PathVisitor(not_hidden, not_hidden).filter_files(src)
    print(*files, sep='\n')
```

----

Copyright &copy; 2025 Karl Knechtel

This project is open source software, distributed under the terms of the MIT License.
Please see `LICENSE.txt` for details.

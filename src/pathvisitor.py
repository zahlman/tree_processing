from functools import partial
from os import PathLike, walk
from pathlib import Path
from shutil import copy
from typing import Any, Callable, NamedTuple, NewType, Optional


# Path.hardlink_to requires 3.10.
# For better compatibility, we fall back to the os module
# and also fall back on copying if hardlinks fail for any reason.
try:
    from os import link as _hardlink
except ImportError: # on MacOS, copy instead.
    hardlink_or_copy = copy
else:
    def hardlink_or_copy(src, dst):
        try:
            _hardlink(src, dst)
        except:
            copy(src, dst)


OnError = NewType('OnError', Optional[Callable[[OSError], Any]])
PathPredicate = NewType('PathPredicate', Callable[[Path], bool])
# The first path is the root of the source file tree;
# the second path is the relative path of the current item
# (file, folder, symlink, ...) relative to the root.
BoundProcessor = NewType('BoundProcessor', Callable[[Path, Path], Any])
# The first path is the root of a destination file tree;
# the next two are as for a BoundProcessor.
FreeProcessor = NewType('FreeProcessor', Callable[[Path, Path, Path], Any])


# A decorator to give FreeProcessors a ".to(dst) method"
# that creates a corresponding BoundProcessor.
def add_dst_binder(fp: FreeProcessor):
    fp.to = lambda p: partial(fp, p)
    return fp


class PathVisitor(NamedTuple):
    process_folder: BoundProcessor
    process_file: BoundProcessor


    def _gen(self, src: PathLike, onerror: OnError, to_yield: int):
        for path, dirs, files in walk(src, onerror=onerror):
            path = Path(path)
            folder = path.relative_to(src)
            if not self.process_folder(src, folder):
                dirs.clear() # ignore child folders
                continue # and files
            for f in files:
                relative = folder / f
                absolute = path / f
                assert absolute == src / relative 
                r = self.process_file(src, relative)
                yield (None, absolute, absolute if r else None, r)[to_yield]


    def process(self, src: PathLike, *, onerror: OnError = None):
        for _ in self._gen(src, onerror, 0):
            pass


    def files(self, src: PathLike, *, onerror: OnError = None):
        yield from self._gen(src, onerror, 1)


    def filter_files(self, src: PathLike, *, onerror: OnError = None):
        yield from filter(None, self._gen(src, onerror, 2))


    def results(self, src: PathLike, *, onerror: OnError = None):
        yield from self._gen(src, onerror, 3)


    # Just for convenience, and symmetry.
    def filter_results(self, src: PathLike, *, onerror: OnError = None):
        yield from filter(None, self._gen(src, onerror, 3))


def recurse_into_folders(src: Path, item: Path):
    return True


@add_dst_binder
def hardlink_or_copy_files(dst: Path, src: Path, item: Path):
    src, dst = src / item, dst / item
    if not src.is_file():
        raise ValueError(f"non-regular file {src} not supported")
    hardlink_or_copy(src, dst)
    return dst # so that the copied files can be listed by .results


@add_dst_binder
def copy_files(dst: Path, src: Path, item: Path):
    src, dst = src / item, dst / item
    if not src.is_file():
        raise ValueError(f"non-regular file {src} not supported")
    copy(src, dst)
    return dst # so that the copied files can be listed by .results


def _copy_folders(predicate: PathPredicate, dst: Path, src: Path, item: Path):
    if not predicate(src / item):
        return False
    return copy_folder(dst, src, item)


def _bind_predicate_to_copy_folders(predicate: PathPredicate):
    return add_dst_binder(partial(_copy_folders, predicate))


copy_folders = _bind_predicate_to_copy_folders(lambda path: True)
copy_folders.which = _bind_predicate_to_copy_folders

"""Assorted helpers"""

import datetime
import enum
import itertools
import os
import subprocess
import zipfile
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlparse

import settings


def ensure_directory(target: str | Path, /) -> Path:
    """Ensure that the target directory exists, creating it if necessary"""
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def curl(url: str, /, *, destination_directory: str | Path = None) -> Path:
    """Download a file without a lot of fuss"""
    expected_downloaded_file_name = Path(urlparse(url).path).name
    # TODO Use Python standard library instead of external curl?
    subprocess.check_call(["curl", "-gsLRO", url], cwd=destination_directory)
    if destination_directory is None:
        destination_directory = "."
    return Path(destination_directory) / expected_downloaded_file_name


def show_files(*files: str | Path, cwd=None) -> None:
    """Like 'ls -ld'"""
    # TODO Use Python standard library instead of external command
    subprocess.check_call(["ls", "-ld", "--"] + list(map(str, files)), cwd=cwd)


def unzip(zip_file: str | Path, /, *, destination_directory: str | Path = None) -> None:
    """Unzip a file"""
    with zipfile.ZipFile(zip_file) as f:
        f.extractall(path=destination_directory)


def rm_v(
    *files: str | Path,
    globs: Iterable[str] = (),
    rglobs: Iterable[str] = (),
    base_directory: str | Path = None,
    only_if: Callable[[Path], bool] = bool,
) -> list[Path]:
    """Like 'rm -v'"""
    if base_directory is None:
        base_directory = "."
    base_directory = Path(base_directory)
    seen = {}
    removed = []
    for candidate in files:
        candidate_path = Path(candidate)
        if candidate_path not in seen:
            resolved_path = base_directory / candidate_path
            seen[candidate_path] = resolved_path
            if (
                only_if(resolved_path)
                and resolved_path.exists()
                and not resolved_path.is_dir()
            ):
                resolved_path.unlink(missing_ok=True)
                print("removed", repr(str(candidate_path)))
                removed.append(candidate_path)
    for action, collection in (
        (base_directory.glob, globs),
        (base_directory.rglob, rglobs),
    ):
        for glob in collection:
            for removed_item in rm_v(
                *itertools.filterfalse(seen.__contains__, action(glob)),
                base_directory=base_directory,
                only_if=only_if,
            ):
                seen[removed_item] = base_directory / removed_item
                removed.append(removed_item)
    return removed


def compare_file_time_to_expiry(
    f: str | Path,
    comparison: Callable[[float, float], bool],
    expiry: datetime.datetime,
    *,
    st_property: property = os.stat_result.st_mtime,
) -> bool:
    """Compare file's mtime to expiry using comparison"""
    return comparison(
        datetime.datetime.fromtimestamp(st_property.fget(Path(f).stat())), expiry
    )


def file_is_older_than(
    f: str | Path,
    expiry: datetime.datetime,
    *,
    st_property: property = os.stat_result.st_mtime,
) -> bool:
    """Is file older than expiry?"""
    return compare_file_time_to_expiry(f, float.__lt__, expiry, st_property=st_property)


class DownloadCategory(enum.Enum):
    """Download categories"""

    DOWNLOAD = settings.downloads
    UPDATE = settings.updates

    def __init__(self, destination_directory: Path) -> None:
        self.destination_directory = destination_directory


def prepare_for_downloads(
    component_name: str,
    *,
    category: DownloadCategory = DownloadCategory.DOWNLOAD,
) -> Path:
    """Return a destination directory for the named component's downloads"""
    # TODO maybe separate directories for each component?
    return ensure_directory(category.destination_directory)

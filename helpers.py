"""Assorted helpers"""

import datetime
import enum
import itertools
import os
import subprocess
import zipfile
from pathlib import Path
from typing import Callable, Iterable

import settings


def ensure_directory(target: str | Path, /) -> Path:
    """Ensure that the target directory exists, creating it if necessary"""
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def curl(
    url: str,
    /,
    *,
    downloaded_file_path: Path = None,
) -> Path:
    """Download a file without a lot of fuss"""
    # TODO Use Python standard library instead of external curl?
    args = ["curl", "--write-out", r"%{filename_effective}\n", "-gsLR"]
    if downloaded_file_path is None:
        destination_directory = Path(".")
        args += ["--remote-header-name", "--remote-name-all"]
    else:
        destination_directory = downloaded_file_path.parent
        args += ["-o", str(downloaded_file_path)]
    args += [url]
    effective_filenames = subprocess.check_output(
        args,
        cwd=destination_directory,
        encoding="utf-8",
    ).splitlines()
    if not effective_filenames:
        raise ValueError(
            "no effective filenames reported from curl", url, downloaded_file_path
        )
    return destination_directory / effective_filenames[0]


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
    st_time_property: property = os.stat_result.st_mtime,
) -> bool:
    """Compare file's mtime to expiry using comparison"""
    filestats = Path(f).stat()
    filetime = st_time_property.__get__(filestats)
    return comparison(filetime, expiry.timestamp())


def file_is_older_than(
    f: str | Path,
    expiry: datetime.datetime,
    *,
    st_time_property: property = os.stat_result.st_mtime,
) -> bool:
    """Is file older than expiry?"""
    return compare_file_time_to_expiry(
        f,
        float.__lt__,
        expiry,
        st_time_property=st_time_property,
    )


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


def metadata_using_exiftool(path: str | Path) -> dict[str, str]:
    """Extract metadata using exiftool"""
    exiftool_output = subprocess.check_output(
        ["exiftool", "-S", "--", str(path)],
        env=dict(TZ="UTC"),
        encoding="utf-8",
    )
    exiftool_lines = exiftool_output.splitlines()
    metadata = {}
    for i, line in enumerate(exiftool_lines):
        parts = line.split(":", maxsplit=1)
        if len(parts) == 2:
            name = parts[0].strip()
            value = parts[1].strip()
            metadata[name] = value
        else:
            raise ValueError("unexpected exiftool format", path, i, line)
    return metadata

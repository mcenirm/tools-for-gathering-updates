"""Assorted helpers"""
import subprocess
import zipfile
from pathlib import Path
from urllib.parse import urlparse


def ensure_directory(target: str | Path, /) -> Path:
    """Ensure that the target directory exists, creating it if necessary"""
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def curl(url: str, /, *, destination_directory: str | Path = None) -> Path:
    """Download a file without a lot of fuss"""
    cwd = Path(destination_directory)
    expected_downloaded_file_name = Path(urlparse(url).path).name
    # TODO Use Python standard library instead of external curl?
    subprocess.check_call(["curl", "-gsLRO", url], cwd=cwd)
    return cwd / expected_downloaded_file_name


def show_files(*files: str | Path, cwd=None) -> None:
    """Like 'ls -ld'"""
    # TODO Use Python standard library instead of external command
    subprocess.check_call(["ls", "-ld", "--"] + list(map(str, files)), cwd=cwd)


def unzip(zip_file: str | Path, /, *, destination_directory: str | Path = None) -> None:
    """Unzip a file"""
    with zipfile.ZipFile(zip_file) as f:
        f.extractall(path=destination_directory)

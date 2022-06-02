"""Assorted helpers"""

from pathlib import Path
from subprocess import CalledProcessError, check_call
from urllib.parse import urlparse


def ensure_directory(target: str | Path, /) -> Path:
    """Ensure that the target directory exists, creating it if necessary"""
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def run(args: list[str], /, *, cwd=None) -> bool:
    """Run an external command without a lot of fuss"""
    try:
        check_call(args, cwd=cwd)
        return True
    except CalledProcessError:
        return False


def curl(url: str, /, *, destination_directory=str | Path) -> Path:
    """Download a file without a lot of fuss"""
    # TODO Use Python standard library instead of external curl?
    expected_downloaded_file_name = Path(urlparse(url).path).name
    check_call(["curl", "-gsLRO", url], cwd=destination_directory)
    return Path(destination_directory) / expected_downloaded_file_name


def show_files(*files: str | Path, cwd=None) -> None:
    """Like 'ls -ld'"""
    # TODO Use Python standard library instead of external command
    check_call(["ls", "-ld", "--"] + list(map(str, files)), cwd=cwd)

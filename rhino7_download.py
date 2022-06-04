"""Download Rhino 7"""

import io
from subprocess import CalledProcessError, check_call

import helpers
import settings

destination_directory = helpers.prepare_for_downloads("wsusoffline")


def check_file() -> bool:
    """Run sha256sum on the downloaded Rhino 7 file"""
    # TODO use Python standard library instead of extern sha256sum
    checksum_input = io.StringIO(
        f"{settings.rhino7_installer_sha256}  {settings.rhino7_installer_file}\n"
    )
    try:
        check_call(
            ["sha256sum", "-c", "-"], cwd=destination_directory, stdin=checksum_input
        )
        return True
    except CalledProcessError:
        return False


if check_file():
    # file already passes, no need to download it
    ...
else:
    # try to download it
    local_copy = helpers.curl(
        settings.rhino7_installer_url, destination_directory=destination_directory
    )
    helpers.show_files(local_copy)

    # check again
    if not check_file():
        raise RuntimeError("TODO bad checksum status?")

"""Download Rhino 7"""

import io
import subprocess

import kits.helpers as helpers
import settings

destination_directory = helpers.prepare_for_downloads("wsusoffline")


def check_file() -> bool:
    """Run sha256sum on the downloaded Rhino 7 file"""
    # TODO use Python standard library instead of extern sha256sum
    checksum_input = (
        settings.rhino7_installer_sha256 + "  " + settings.rhino7_installer_file + "\n"
    ).encode("utf-8")
    completed_process = subprocess.run(
        ["sha256sum", "-c", "-"],
        cwd=destination_directory,
        input=checksum_input,
    )
    return 0 == completed_process.returncode


if check_file():
    # file already passes, no need to download it
    ...
else:
    # try to download it
    local_copy = helpers.curl(
        settings.rhino7_installer_url,
        downloaded_file_path=destination_directory / settings.rhino7_installer_file,
    )
    helpers.show_files(local_copy)

    # check again
    if not check_file():
        raise RuntimeError("TODO bad checksum status?")

"""Download WSUS Offline Community Edition"""

from subprocess import CalledProcessError, check_call

import helpers
import settings

destination_directory = helpers.prepare_for_downloads("wsusoffline")


def check_files() -> bool:
    """Run hashdeep on the downloaded WSUS Offline files"""
    try:
        check_call(
            [
                "hashdeep",
                "-s",
                "-a",
                "-l",
                "-k",
                settings.wsusoffline_hashes_file,
                settings.wsusoffline_zip_file,
            ],
            cwd=destination_directory,
        )
        return True
    except CalledProcessError:
        return False


if check_files():
    # files already pass, no need to download them
    ...
else:
    # try to download them
    for u in [settings.wsusoffline_hashes_url, settings.wsusoffline_zip_url]:
        local_copy = helpers.curl(u, destination_directory=destination_directory)
        helpers.show_files(local_copy)

    # check again
    if not check_files():
        raise RuntimeError("TODO bad hashdeep status?")

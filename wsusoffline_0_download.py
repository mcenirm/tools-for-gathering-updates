"""Download WSUS Offline Community Edition"""

import subprocess

import kits.helpers as helpers
import settings

destination_directory = helpers.prepare_for_downloads("wsusoffline")


def check_files() -> bool:
    """Run hashdeep on the downloaded WSUS Offline files"""
    completed_process = subprocess.run(
        [
            "hashdeep",
            "-s",
            "-a",
            "-l",
            "-k",
            settings.wsusoffline_hashes_file,
            settings.wsusoffline_zip_file,
        ],
        check=True,
        cwd=destination_directory,
    )
    return 0 == completed_process.returncode


if check_files():
    # files already pass, no need to download them
    ...
else:
    # try to download them
    for filename, url in [
        (settings.wsusoffline_hashes_file, settings.wsusoffline_hashes_url),
        (settings.wsusoffline_zip_file, settings.wsusoffline_zip_url),
    ]:
        local_copy = helpers.curl(
            url,
            downloaded_file_path=destination_directory / filename,
        )
        helpers.show_files(local_copy)

    # check again
    if not check_files():
        raise RuntimeError("TODO bad hashdeep status?")

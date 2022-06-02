"""Download WSUS Offline Community Edition"""

import helpers
import settings


def check_files():
    """Run hashdeep on the downloaded WSUS Offline files"""
    return helpers.run(
        [
            "hashdeep",
            "-s",
            "-a",
            "-l",
            "-k",
            settings.wsusoffline_hashes_file,
            settings.wsusoffline_zip_file,
        ],
        cwd=settings.downloads,
    )


helpers.ensure_directory(settings.downloads)
if check_files():
    # files already pass, no need to download them
    ...
else:
    # try to download them
    for u in [settings.wsusoffline_hashes_url, settings.wsusoffline_zip_url]:
        local_copy = helpers.curl(u, destination_directory=settings.downloads)
        helpers.show_files(local_copy)

    # check again
    if not check_files():
        raise RuntimeError("TODO bad hashdeep status?")

"""Download latest Nessus plugin set"""

import contextlib
from urllib.request import urlopen

import helpers
import settings

# get latest plugin set version
with urlopen(settings.nessus_plugin_version_url) as f:
    nessus_plugin_latest_version = f.read().decode()

nessus_plugin_name = (
    f"{settings.nessus_plugin_dir_prefix}{nessus_plugin_latest_version}"
)
nessus_plugin_dir = settings.nessus_updates_dir / nessus_plugin_name
nessus_plugin_file_downloaded = nessus_plugin_dir / settings.nessus_plugin_file_name

if not nessus_plugin_file_downloaded.exists():
    destination_directory = helpers.ensure_directory(nessus_plugin_dir)
    downloaded_file = helpers.curl(
        settings.nessus_plugin_url, destination_directory=destination_directory
    )
    downloaded_file.rename(nessus_plugin_file_downloaded)

details_out = open(
    settings.nessus_plugin_details_file,
    mode="w",
    encoding="utf-8",
)
with details_out, contextlib.redirect_stdout(details_out):
    print(f"nessus_plugin_latest_version={repr(str(nessus_plugin_latest_version))}")
    print(f"nessus_plugin_file_downloaded={repr(str(nessus_plugin_file_downloaded))}")
    print(f"nessus_plugin_dir={repr(str(nessus_plugin_dir))}")
    print(f"nessus_plugin_name={repr(str(nessus_plugin_name))}")

helpers.show_files(nessus_plugin_file_downloaded)

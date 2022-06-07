"""Prepare monthly security updates DVD"""

import pathlib
import shutil
import subprocess
import sys

import settings
from prepare_common import DVD

dvd = DVD("monthly", "Monthly Security", "Windows updates")

subprocess.run([sys.executable, "wsusoffline_2_getupdates.py"], check=True)
subprocess.run([sys.executable, "wsusoffline_3_prune_updates.py"], check=True)

wsusoffline_dvd_client_dir_name = "wsusofflineclient"

shutil.copytree(
    settings.wsusoffline_client_dir,
    dvd.dir / wsusoffline_dvd_client_dir_name,
)

dvd.append_to_install_instructions(
    f"""

# Install Windows updates

1. Open an admin PowerShell, change to the optical drive, and run the command:

    & '{pathlib.PureWindowsPath(wsusoffline_dvd_client_dir_name)}\\UpdateInstaller.exe'

TODO document weird "screensaver" thing it does

"""
)

dvd.show_instructions()

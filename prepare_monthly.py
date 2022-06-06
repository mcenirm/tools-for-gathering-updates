"""Prepare monthly security updates DVD"""

import pathlib
import shutil
import subprocess
import sys

import helpers
import settings
from prepare_common import DVD

dvd = DVD("monthly", "Monthly Security", "Windows updates")

subprocess.check_call(sys.executable, "wsusoffline_2_getupdates.py")
subprocess.check_call(sys.executable, "wsusoffline_3_prune_updates.py")

wsusoffline_dvd_client_dir_name = "wsusofflineclient"
wsusoffline_dvd_client_dir = helpers.ensure_directory(
    dvd.dir / wsusoffline_dvd_client_dir_name
)

shutil.copytree(settings.wsusoffline_client_dir, wsusoffline_dvd_client_dir)

dvd.append_to_install_instructions(
    f"""

# Install Windows updates

1. Open an admin PowerShell, change to the optical drive, and run the command:

    & '{pathlib.PureWindowsPath(wsusoffline_dvd_client_dir_name)}\\UpdateInstaller.exe'

TODO document weird "screensaver" thing it does

"""
)

dvd.show_instructions()

"""Prepare weekly security updates DVD"""

import pathlib
import shutil
import subprocess
import sys

import helpers
import settings
from prepare_common import DVD

weekly_dvd = DVD("weekly", "Weekly Security", "AV signatures", "Nessus plugin")

# get updates

subprocess.run([sys.executable, "wsusoffline_2_getupdates.py"], check=True)

mpamfe_file_name = "mpam-fe.exe"
mpamfe_file = settings.wsusoffline_client_dir / f"wddefs/x64-glb/{mpamfe_file_name}"
mpamfe_metadata = helpers.metadata_using_exiftool(mpamfe_file)
mpamfe_version = mpamfe_metadata["ProductVersionNumber"]
mpamfe_date = mpamfe_metadata["TimeStamp"].split()[0].replace(":", "-")
mpamfe_dir_name = f"windows-defender-{mpamfe_date}-{mpamfe_version}"

subprocess.run([sys.executable, "nessus_2_getupdates.py"], check=True)
nessus_details = {}
with open(settings.nessus_plugin_details_file, encoding="utf-8") as f:
    for line in f:
        key, value = line.split("=", maxsplit=1)
        nessus_details[key.strip()] = value.strip()

# add contents to DVD folder
mpamfe_dvd_dir = helpers.ensure_directory(weekly_dvd.dir / mpamfe_dir_name)
shutil.copy2(mpamfe_file, mpamfe_dvd_dir)
mpamfe_exe_windows_path = pathlib.PureWindowsPath(mpamfe_dir_name, mpamfe_file_name)
weekly_dvd.append_to_install_instructions(
    f"""

# Update the Windows Defender definitions

1. Open an admin PowerShell, change to the optical drive, and run the command:

    & '{mpamfe_exe_windows_path}' -q

2. Verify the definition date in Windows Security
   ("Virus & threat protection", "Virus & threat protection updates")

Note: The GUI takes a few minutes before it shows the new definition date / version.

"""
)

nessus_dvd_dir = helpers.ensure_directory(
    weekly_dvd.dir / nessus_details["nessus_plugin_name"]
)
shutil.copy2(nessus_details["nessus_plugin_file_downloaded"], nessus_dvd_dir)
nessus_plugin_set_windows_path = pathlib.PureWindowsPath(
    nessus_details["nessus_plugin_name"],
    settings.nessus_plugin_file_name,
)
weekly_dvd.append_to_install_instructions(
    f"""

# Nessus plugin set

Update the Nessus plugin set:

1. Open Nessus web console https://localhost:8834/

2. "Settings" (from the top menu)

3. "Software Update" (tab)

4. "Manual Software Update" (button, top right)

5. "Upload your own plugin archive" (radio button choice)

6. "Continue" (button)

7. Browse to "{nessus_plugin_set_windows_path}" and "Open"

8. TODO Document the behavior (eg, the spinner bottom left)

9. "Overview" (tab)

10. Wait about 20 minutes. (This is a good time to run the Windows Defender full scan.)

11. Every 5 minutes, refresh the page until "Plugin Set" (right side) matches the new version.

"""
)

weekly_dvd.show_instructions()


# TODO
# * automate
#    * check for updates
#    * download updates
#    * generate documented procedures for installing updates on target systems
#    * prepare folders to be burned to DVD
#    * generate documented procedures for burning folders to DVD
#    * notify humans
# * different frequencies for different needs
#    * weekly - antivirus definitions
#    * monthly - security updates ("Patch Tuesday")
#    * quarterly - compliance benchmarks
#    * yearly - ???
# * folders to be burned to DVD
#    * handle DVD capacity limitations
#    * include integrity manifests
#    * include instructions for humans
#    * include automated checks (eg, before vs after versions)
#    * include report/summary generator to run on target systems

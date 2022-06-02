#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.py
. "$here"/prepare-common.py

_dvd_init weekly 'Weekly Security' 'AV signatures' 'Nessus plugin'

# get updates

$here/wsusoffline_2_getupdates.py
mpamfe_file_name=mpam-fe.exe
mpamfe_file=$wsusoffline_client_dir/wddefs/x64-glb/$mpamfe_file_name
mpamfe_version=$(exiftool -S -s -ProductVersionNumber -- "$mpamfe_file")
mpamfe_date=$(TZ=UTC exiftool -S -s -TimeStamp -- "$mpamfe_file" | sed -e 's/ .*$//' -e 's/:/-/g')
mpamfe_dir_name=windows-defender-$mpamfe_date-$mpamfe_version
mpamfe_dvd_dir=$dvd_dir/$mpamfe_dir_name

$here/nessus-2-getupdates.py
. "$nessus_plugin_details_file"
nessus_dvd_dir=$dvd_dir/$nessus_plugin_name

# add contents to DVD folder

mkdir -pv -- "$mpamfe_dvd_dir"
cp -pv -- "$mpamfe_file" "$mpamfe_dvd_dir/"
cat >> "$dvd_install_instructions" <<EOF

# Update the Windows Defender definitions

1. Open an admin PowerShell, change to the optical drive, and run the command:

    & '$mpamfe_dir_name\\$mpamfe_file_name' -q

2. Verify the definition date in Windows Security
   ("Virus & threat protection", "Virus & threat protection updates")

Note: The GUI takes a few minutes before it shows the new definition date / version.

EOF

mkdir -pv -- "$nessus_dvd_dir"
cp -pv -- "$nessus_plugin_file_downloaded" "$nessus_dvd_dir/"
cat >> "$dvd_install_instructions" <<EOF

# Nessus plugin set

Update the Nessus plugin set:

1. Open Nessus web console https://localhost:8834/

2. "Settings" (from the top menu)

3. "Software Update" (tab)

4. "Manual Software Update" (button, top right)

5. "Upload your own plugin archive" (radio button choice)

6. "Continue" (button)

7. Browse to "$nessus_plugin_name\\$nessus_plugin_file_name" and "Open"

8. TODO Document the behavior (eg, the spinner bottom left)

9. "Overview" (tab)

10. Wait about 20 minutes. (This is a good time to run the Windows Defender full scan.)

11. Every 5 minutes, refresh the page until "Plugin Set" (right side) matches the new version.

EOF

cat <<EOF
---------- Installation instructions -----------------------
$(cat -- "$dvd_install_instructions")
------------------------------------------------------------

---------- Burn and scan instructions ----------------------
$(cat -- "$dvd_burn_and_scan_instructions")
------------------------------------------------------------
EOF


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

#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.bash
. "$here"/prepare-common.bash

_dvd_init monthly 'Monthly Security' 'Windows updates'

$here/wsusoffline-2-getupdates.bash
$here/wsusoffline-3-prune-updates.bash

wsusoffline_dvd_client_dir_name=wsusofflineclient
wsusoffline_dvd_client_dir=$dvd_dir/$wsusoffline_dvd_client_dir_name

mkdir -pv -- "$wsusoffline_dvd_client_dir"
cp -prT -- "$wsusoffline_client_dir" "$wsusoffline_dvd_client_dir"

cat > "$dvd_install_instructions" <<EOF

# Install Windows updates

1. Open an admin PowerShell, change to the optical drive, and run the command:

    & '$wsusoffline_dvd_client_dir_name\\UpdateInstaller.exe'

TODO document weird "screensaver" thing it does

EOF

cat <<EOF
---------- Installation instructions -----------------------
$(cat -- "$dvd_install_instructions")
------------------------------------------------------------

---------- Burn and scan instructions ----------------------
$(cat -- "$dvd_burn_and_scan_instructions")
------------------------------------------------------------
EOF

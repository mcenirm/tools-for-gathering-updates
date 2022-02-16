#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.bash

dvd_dir=$base/dvd-$(date -u +%Y%m%d)-weekly
dvd_readme=$dvd_dir/README.txt

if [ -d "$dvd_dir" ]
then
  echo >&2 "ERROR: target DVD directory already exists: $dvd_dir"
  exit 1
fi

# get updates

$here/wsusoffline-2-getupdates.bash
mpamfe_file_name=mpam-fe.exe
mpamfe_file=$wsusoffline_client_dir/wddefs/x64-glb/$mpamfe_file_name
mpamfe_version=$(exiftool -S -s -ProductVersionNumber -- "$mpamfe_file")
mpamfe_date=$(TZ=UTC exiftool -S -s -TimeStamp -- "$mpamfe_file" | sed -e 's/ .*$//' -e 's/:/-/g')
mpamfe_dir_name=windows-defender-$mpamfe_date-$mpamfe_version
mpamfe_dvd_dir=$dvd_dir/$mpamfe_dir_name

$here/nessus-2-getupdates.bash
. "$nessus_plugin_details_file"
nessus_dvd_dir=$dvd_dir/$nessus_plugin_name

# prepare folder for DVD

mkdir -pv -- "$mpamfe_dvd_dir"
cp -pv -- "$mpamfe_file" "$mpamfe_dvd_dir/"
cat >> "$dvd_readme" <<EOF
Update the Windows Defender definitions using:

    & '$mpamfe_dir_name\\$mpamfe_file_name' -q

EOF

mkdir -pv -- "$nessus_dvd_dir"
cp -pv -- "$nessus_plugin_file_downloaded" "$nessus_dvd_dir/"
cat >> "$dvd_readme" <<EOF
Update the Nessus plugin set using:

    & 'C:\\Program Files\\Tenable\\Nessus\\nessuscli.exe' update '$nessus_plugin_name\\$nessus_plugin_file_name'

EOF

printf '%s\n' ------------------------------------------------------------
cat -- "$dvd_readme"
printf '%s\n' ------------------------------------------------------------

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

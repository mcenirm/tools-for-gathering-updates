#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.py

mkdir -pv -- "$nessus_updates_dir"
cd -- "$nessus_updates_dir"

# get latest plugin set version
nessus_plugin_latest_version=$(curl -gs "$nessus_plugin_version_url")
nessus_plugin_name=$nessus_plugin_dir_prefix$nessus_plugin_latest_version
nessus_plugin_dir=$nessus_updates_dir/$nessus_plugin_name
nessus_plugin_file_downloaded=$nessus_plugin_dir/$nessus_plugin_file_name

if ! [ -e "$nessus_plugin_file_downloaded" ]
then
  mkdir -pv -- "$nessus_plugin_dir"
  curl -gsLRo "$nessus_plugin_file_downloaded" "$nessus_plugin_url"
fi
(
  printf '%q\n' "nessus_plugin_latest_version=$nessus_plugin_latest_version"
  printf '%q\n' "nessus_plugin_file_downloaded=$nessus_plugin_file_downloaded"
  printf '%q\n' "nessus_plugin_dir=$nessus_plugin_dir"
  printf '%q\n' "nessus_plugin_name=$nessus_plugin_name"
) > "$nessus_plugin_details_file"

ls -ld -- "$nessus_plugin_file_downloaded"

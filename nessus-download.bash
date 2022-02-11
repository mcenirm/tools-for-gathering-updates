#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.bash

mkdir -pv -- "$downloads"
cd -- "$downloads"

# get latest plugin set version
nessus_plugin_latest_version=$(curl -gs "$nessus_plugin_version_url")
nessus_plugin_dir=$nessus_plugin_dir_prefix$nessus_plugin_latest_version
nessus_plugin_file_downloaded=$nessus_plugin_dir/$nessus_plugin_file

if ! [ -e "$nessus_plugin_file_downloaded" ]
then
  mkdir -pv -- "$nessus_plugin_dir"
  curl -gsLRo "$nessus_plugin_file_downloaded" "$nessus_plugin_url"
  ls -ld -- "$nessus_plugin_file_downloaded"
fi

#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.py

mkdir -pv -- "$downloads"
cd -- "$downloads"

downloaded_once=false
until echo "$rhino7_installer_sha256  $rhino7_installer_file" | sha256sum -c -
do
  if $downloaded_once ; then exit 1 ; fi
  for u in "$rhino7_installer_url"
  do
    curl -gsLRO "$u"
    ls -ld -- "${u##*/}"
  done
  downloaded_once=true
done

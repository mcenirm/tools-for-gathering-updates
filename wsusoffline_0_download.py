#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.py

mkdir -pv -- "$downloads"
cd -- "$downloads"

downloaded_once=false
until hashdeep -s -a -l -k "$wsusoffline_hashes_file" "$wsusoffline_zip_file"
do
  if $downloaded_once ; then exit 1 ; fi
  for u in "$wsusoffline_hashes_url" "$wsusoffline_zip_url"
  do
    curl -gsLRO "$u"
    ls -ld -- "${u##*/}"
  done
  downloaded_once=true
done

#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.py

mkdir -pv -- "$updates"
cd -- "$updates"

unzip -q $downloads/$wsusoffline_zip_file
cd wsusoffline/sh

# avoid pinging external system
# TODO avoid pinging at all
sed -i -e 's/ www.wsusoffline.net / localhost /' common-tasks/40-configure-downloaders.bash

bash fix-file-permissions.bash

for n in update-generator.ini windows-10-versions.ini
do
  cp -ipv "$files/wsusoffline-$n" "./$n"
done

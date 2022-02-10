#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.bash

cd -- "$updates/wsusoffline/sh"

# TODO
# Add option to force updates for some or all categories,
# even if done recently (see "sh/libraries/timestamps.bash")
#  * remove timestamps/timestamp*.txt
#  * (UNTESTED) remove client/md/hashes*.txt to avoid warnings about integrity database

./download-updates.bash w100-x64 enu -includesp -includecpp -includedotnet -includewddefs

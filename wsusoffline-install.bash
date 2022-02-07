#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.bash

mkdir -pv -- "$updates"
cd -- "$updates"

unzip $downloads/$wsusoffline_zip_file

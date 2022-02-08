#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.bash

cd -- "$updates/wsusoffline/client/w100-x64/glb"

# remove update files for KB numbers that we ignore
# (eg, due to wrong Windows 10 version not being filtered out)
shopt -s nullglob
for kb in "${kb_ignores[@]}"
do
  kbcabs=(*-"kb$kb"-*.cab)
  if [ ${#kbcabs[*]} -gt 0 ]
  then
    rm -v -- "${kbcabs[@]}"
  fi
done

# remove any update files that are old enough
# that they should have been applied already
find . -type f -name '*-kb[0-9]*' -mtime +"$kb_prune_days" -print0 \
| xargs -r -0 rm -v --

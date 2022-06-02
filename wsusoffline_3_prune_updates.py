#!/bin/bash
set -euo pipefail

. "$(dirname -- "$BASH_SOURCE")"/settings.py

cd -- "$wsusoffline_client_dir"

# let arrays be empty if there are no matching files
shopt -s nullglob

# remove update files for KB numbers that we ignore
# (eg, due to wrong Windows 10 version not being filtered out)
for kb in "${kb_ignores[@]}"
do
  kbcabs=(w100-x64/glb/*-"kb$kb"-*.cab)
  if [ ${#kbcabs[*]} -gt 0 ]
  then
    rm -v -- "${kbcabs[@]}"
  fi
done

# remove other update files that are known to be unneeded
# (mostly 32-bit files when 64-bit options also exist)
others=(
    cpp/vcredist*_x86.exe
    dotnet/aspnetcore-runtime-*-win-x86.exe
    dotnet/dotnet-runtime-*-win-x86.exe
    dotnet/windowsdesktop-runtime-*-win-x86.exe
    msedge/MicrosoftEdgeUpdateSetup_X86_*.exe
    msedge/MicrosoftEdge_X86_*.exe
)
if [ ${#others[*]} -gt 0 ]
then
  rm -v -- "${others[@]}"
fi

# remove any update files that are old enough
# that they should have been applied already
paths_to_check=(
    cpp
    dotnet
    msedge
    w100-x64/glb
)
find "${paths_to_check[@]}" \
    -type f \
    \( -name '*.cab' -o -name '*.exe' -o -name '*.msu' \) \
    -mtime +"$wsusoffline_prune_days" \
    -print0 \
| xargs -r -0 rm -v --

#!/usr/bin/env bash
# vim: shiftwidth=2 tabstop=2 expandtab
set -euo pipefail
[[ "${TRACE-0}" == "1" ]] && set -x

default_days=45
Usage () { cat >&2 <<EOF
Usage: $0
Gather updates and show recent items
Options:
  --skip-gather    just show the recent items
  --days=N         define "recent" [$default_days]
EOF
}
UsageExit () { Usage ; exit 1 ; }


cd -- "$(dirname -- "$BASH_SOURCE")"

days=$default_days
skip_gather=false
while [ $# -gt 0 ]
do
  case "$1" in
    --skip-gather) skip_gather=true ; shift ;;
    --days=*)
      days=${1#--days=}
      [[ "$days" =~ ^[0-9]+$ ]] || UsageExit
      shift
      ;;
    *) UsageExit ;;
  esac
done

failed=()
if ! $skip_gather
then
  for dx in ./download-*.bash ./*-download.bash ./*-getupdates.bash
  do
    if ! "$dx"
    then
      failed+=( "$dx" )
    fi
  done
fi

(
  for dir in ../updates/wsusoffline/client/ ../downloads/ ../updates/nessus/
  do
    (
      cd "$dir/.."
      find "$(basename -- "$dir")" -type f -mtime -"$days" -print0 | xargs -0 -r du -h --time
    )
  done
)                                              \
| grep -E -i -e '\.(cab|crt|exe|msi|tar\.gz)$' \
| sort -k2                                     \
| sed -r                                       \
      -e $'s#\\b(client/)#\\1\E[35;1m#'        \
      -e $'s#\\b(downloads/)#\\1\E[36;1m#'     \
      -e $'s/$/\E[0m/'

if [ ${#failed[@]} -gt 0 ]
then
  echo FAILED:
  printf ' - %s\n' "${failed[@]}"
fi

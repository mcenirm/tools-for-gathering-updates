#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "$BASH_SOURCE")"

this=$(basename -- "${BASH_SOURCE}")
name=${this%.bash}
if [ "$name" != 'legacy-wrapper' ]
then
  pyname=${name//-/_}.py
  exec conda run -p ../conda_env --no-capture-output --live-stream python "$pyname" "$@"
else
  wrappers=(
      nessus-2-getupdates.bash
      prepare-monthly.bash
      prepare-weekly.bash
      rhino7-download.bash
      wsusoffline-0-download.bash
      wsusoffline-1-install.bash
      wsusoffline-2-getupdates.bash
      wsusoffline-3-prune-updates.bash
  )
  usage () {
    cat >&2 <<EOF
Usage: ./legacy-wrapper.bash ACTION
Manage legacy bash wrappers for python scripts

Actions:
  clean        Remove wrappers
  list         List wrappers
  rebuild      Rebuild wrappers

Options:
  --dry-run    Show what would happen
EOF
  }
  dryrun=false
  while [ $# -gt 0 ]
  do
    case "$1" in
    --dry-run) dryrun=true ; shift ;;
    -*) usage ; exit 1 ;;
    *) break ;;
    esac
  done
  [ $# -gt 0 ] || { usage ; exit 1 ; }
  case "$1" in
  clean|list|rebuild) action=$1 ; shift ;;
  *) usage ; exit 1 ;;
  esac
  args=()
  while [ $# -gt 0 ]
  do
    case "$1" in
    --dry-run) dryrun=true ; shift ;;
    -*) usage ; exit 1 ;;
    *) args+=( "$1" ) ; shift ;;
    esac
  done

  clean () {
    local wrappers_to_remove=()
    local w
    for w in "${wrappers[@]}"
    do
      [ -e "$w" ] && wrappers_to_remove+=( "$w" )
    done
    if [ "${#wrappers_to_remove[@]}" -lt 1 ]
    then
      printf 'nothing to remove\n'
    else
      if $dryrun
      then
        printf 'would remove: %q\n' "${wrappers_to_remove[@]}"
      else
        rm -v -- "${wrappers_to_remove[@]}"
      fi
    fi
  }

  list () {
    printf '%s\n' "${wrappers[@]}"
  }

  rebuild () {
    local w
    if $dryrun
    then
      printf 'would link: %q\n' "${wrappers[@]}"
    else
      for w in "${wrappers[@]}"
      do
        ln -vf -- "$this" "$w"
      done
    fi
  }

  if [ "${#args[@]}" -lt 1 ]
  then
    "$action"
  else
    "$action" "${args[@]}"
  fi
fi

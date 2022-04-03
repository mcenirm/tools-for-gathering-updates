# initialize setup for a DVD
# parameters:
#   - tag
#   - label
#   - [item...]
# example call:  _dvd_init weekly 'Weekly Security' 'AV signatures' 'Nessus plugin'
_dvd_init () {
  local tag=''
  if [ $# -gt 1 ]
  then
    tag=$1
    shift
  fi
  if [ -z "$tag" ]
  then
    echo >&2 "ERROR: '_dvd_init' called with empty tag from: ${BASH_SOURCE[1]}"
    return 1
  fi

  local label=''
  if [ $# -gt 1 ]
  then
    label=$1
    shift
  fi
  if [ -z "$label" ]
  then
    echo >&2 "ERROR: '_dvd_init' called with empty label from: ${BASH_SOURCE[1]}"
    exit 1
  fi

  # global variables
  dvd_tag=$tag
  dvd_label=$label
  dvd_date=$(date -u +%Y%m%d)
  dvd_dir=$dvds/dvd-$dvd_date-$tag
  dvd_install_instructions=$dvd_dir/INSTALL.txt
  dvd_burn_and_scan_instructions=$dvd_dir-BURN_AND_SCAN.txt
  dvd_scan_report=$dvd_dir-scan.log

  # sanity checks
  if [ -d "$dvd_dir" ]
  then
    echo >&2 "ERROR: target DVD directory already exists: $dvd_dir"
    exit 1
  fi

  # build dvd tree
  mkdir -pv -- "$dvd_dir"

  # prepare burn and scan instructions
  cat > "$dvd_burn_and_scan_instructions" <<EOF

1.  Insert a blank DVD in the optical drive.

2.  Burn the folder to the disc.

    growisofs -dvd-compat -Z "$dvd_device" -verbose \\
        -iso-level 4 -joliet -joliet-long -rational-rock -udf \\
        "$dvd_dir"

3.  Wait for the disc ejection after the burning completes.

4.  Reinsert the disc.

5.  As root, mount the DVD contents.

    mount -v -o ro -- "$dvd_device" "$dvd_mountpoint"

6.  As non-root, run the scan.

    (cd -- "$dvd_mountpoint" && clamscan -v -a -r --log="$dvd_scan_report" .)

7.  As root, unmount and eject the disc.

    eject -v -- "$dvd_mountpoint"

8.  Label the DVD.

    $dvd_label  $dvd_date
EOF
  if [ $# -gt 0 ]
  then
    for item in "$@"
    do
      echo "    - $item" >> "$dvd_burn_and_scan_instructions"
    done
  fi
  echo >> "$dvd_burn_and_scan_instructions"

}

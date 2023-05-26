#!/bin/bash
set -euo pipefail

installer_listing_url='https://www.tenable.com/downloads/nessus?loginAttempted=true'

installer_listing_name='nessus-installer-listing'
installer_listing_dl=metadata/${installer_listing_name}.html
installer_listing_xhtml=metadata/${installer_listing_name}.xhtml
installer_listing_json=metadata/${installer_listing_name}.json
latest_json=metadata/nessus-win64-msi.json


error () {
  printf >&2 ERROR:
  printf >&2 ' %s' "$@"
  printf >&2 '\n'
  exit 1
}


cd -- "$(dirname -- "$BASH_SOURCE")/../downloads"
need_installer_listing_dl=true
if [ -f "${installer_listing_dl}" ]
then
  if [ $(stat -c %Y "${installer_listing_dl}") -gt $(date -d '12 hours ago' +%s) ]
  then
    need_installer_listing_dl=false
  fi
fi
if ${need_installer_listing_dl}
then
  curl -sLRgo "${installer_listing_dl}" "${installer_listing_url}"
fi
tidy -quiet --show-warnings no -numeric --output-xml yes -output "${installer_listing_xhtml}" "${installer_listing_dl}" || tidy_status=$?
if [ $tidy_status -gt 1 ]
then
  exit $tidy_status
fi
xmlstarlet select \
    --text \
    --template \
    --match "//script[@id='__NEXT_DATA__']" \
    --value-of 'text()' \
    "${installer_listing_xhtml}" \
    | tail -n+2 \
    | perl -00 -ple 's#\n##g' \
    > "${installer_listing_json}"
cat "${installer_listing_json}" \
| jq -S '
.props.pageProps.products
| with_entries(select(.key|match("^nessus-10\\.";"i")))[]
.downloads[]
| select(.name|match("-x64\\.msi$";"i"))
' > "${latest_json}"

latest_file=$(cat "${latest_json}" | jq -r .file)
latest_id=$(cat "${latest_json}" | jq -r .id)

latest_msi_hashalgo=sha256
latest_msi_hash=$(cat "${latest_json}" | jq -r .meta_data."${latest_msi_hashalgo}")
latest_product=$(cat "${latest_json}" | jq -r .meta_data.product)
latest_version=$(cat "${latest_json}" | jq -r .meta_data.version)

latest_msi_dl=${latest_file}
latest_msi_url='https://www.tenable.com/downloads/api/v1/public/pages/nessus/downloads/'${latest_id}'/download?i_agree_to_tenable_license_agreement=true'

latest_msi_cksum_prog=${latest_msi_hashalgo,,}sum
latest_msi_cksum_txt=metadata/${latest_product}.${latest_msi_cksum_prog}.txt
cat > "${latest_msi_cksum_txt}" <<EOF
${latest_msi_hash,,}  ${latest_msi_dl}
EOF
if [ ! -f "${latest_msi_dl}" ]
then
  curl -gLRo "${latest_msi_dl}" "${latest_msi_url}"
fi
"${latest_msi_cksum_prog}" -c "${latest_msi_cksum_txt}"

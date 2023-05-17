#!/bin/bash
set -euo pipefail

api_endpoint='https://api.adoptium.net/' # or staging-api.adoptium.net
param_feature_version='11'
param_release_type='ga' # General Availability vs Early Access
param_os='windows'
param_arch='x64'
param_image_type='jdk'
param_jvm_impl='hotspot'
param_heap_size='normal' # normal or large (?)
param_vendor='eclipse'
 
latest_assets_url="${api_endpoint}/v3/assets/latest/${param_feature_version}/${param_jvm_impl}?architecture=${param_arch}&image_type=${param_image_type}&os=${param_os}&vendor=${param_vendor}"
latest_assets_json=metadata/temurin-${param_feature_version}-${param_jvm_impl}-${param_arch}-${param_image_type}-${param_os}-${param_vendor}.json

json_query_installer='.[0].binary.installer'
json_query_checksum=${json_query_installer}.checksum
json_query_name=${json_query_installer}.name
json_query_link=${json_query_installer}.link

latest_msi_hashalgo='sha256'
latest_msi_cksum_prog=${latest_msi_hashalgo,,}sum


error () {
  printf >&2 ERROR:
  printf >&2 ' %s' "$@"
  printf >&2 '\n'
  exit 1
}


cd -- "$(dirname -- "$BASH_SOURCE")/../downloads"

curl -sgo "${latest_assets_json}" "${latest_assets_url}"

latest_msi_dl=$(cat -- "${latest_assets_json}" | jq -r "${json_query_name}")
case ${latest_msi_dl} in
*.msi) : ;;
*) error 'unexpected ext:' "${latest_msi_dl}" ;;
esac

latest_msi_url=$(cat -- "${latest_assets_json}" | jq -r "${json_query_link}")

latest_msi_hash=$(cat -- "${latest_assets_json}" | jq -r "${json_query_checksum}")
latest_msi_cksum_txt=metadata/${latest_msi_dl}.${latest_msi_cksum_prog}.txt
cat > "${latest_msi_cksum_txt}" <<EOF
${latest_msi_hash,,}  ${latest_msi_dl}
EOF
if [ ! -f "${latest_msi_dl}" ]
then
  curl -gLRo "${latest_msi_dl}" "${latest_msi_url}"
fi
"${latest_msi_cksum_prog}" -c "${latest_msi_cksum_txt}"

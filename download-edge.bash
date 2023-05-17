#!/usr/bin/env bash
# vim: shiftwidth=2 tabstop=2 expandtab
set -euo pipefail
[[ "${TRACE-0}" == "1" ]] && set -x

start_page_url='https://www.microsoft.com/en-us/edge/business/download'

start_page_name='e4bdownload'
start_page_dl=metadata/${start_page_name}.html
start_page=metadata/${start_page_name}.xhtml
start_page_script_prefix=metadata/${start_page_name}.script
start_page_script_suffix=.%d.js
start_page_matching_scripts=${start_page_script_prefix}s.txt
##start_page_js=${start_page_script_prefix}.0.js
start_page_json=metadata/${start_page_name}.json
latest_json=metadata/e4b-windows-x64.json


error () {
  printf >&2 ERROR:
  printf >&2 ' %s' "$@"
  printf >&2 '\n'
  exit 1
}


cd -- "$(dirname -- "$BASH_SOURCE")/../downloads"
need_start_page_dl=true
if [ -f "${start_page_dl}" ]
then
  if [ $(stat -c %Y "${start_page_dl}") -gt $(date -d '12 hours ago' +%s) ]
  then
    need_start_page_dl=false
  fi
fi
if ${need_start_page_dl}
then
  curl -sLRgo "${start_page_dl}" "${start_page_url}"
fi
tidy \
    -quiet \
    --show-warnings no \
    -numeric \
    --wrap 0 \
    --output-xml yes \
    -output "${start_page}" \
    "${start_page_dl}" \
    || tidy_status=$?
if [ $tidy_status -gt 1 ]
then
  echo >&2 ERROR: Problem running tidy: $tidy_status
  exit $tidy_status
fi

###########################

#xmlstarlet select \
#    -N x=http://www.w3.org/1999/xhtml \
#    --text \
#    --template \
#    --match "//x:div[@id='commercial-json-data']" \
#    --value-of @data-whole-json \
#    "${start_page}" \
#    > "${start_page_json}"

#cat "${start_page_json}" \
#| jq -S '
#[
#  .[]
#  |select(.product=="Stable")|.releases[]
#  |select(.architecture=="x64" and .platform=="Windows")
#]
#|sort_by(.releaseId)
#[-1]
#' > "${latest_json}"

#latest_version=$(cat "${latest_json}" | jq -r .productVersion)
#latest_msi_json_data=$(cat "${latest_json}" | jq -c '
#.artifacts[]
#|select(.artifactName == "msi")
#')
#latest_msi_hash=$(jq -r <<<"${latest_msi_json_data}" .hash)
#latest_msi_hashalgo=$(jq -r <<<"${latest_msi_json_data}" .hashAlgorithm)
#latest_msi_url=$(jq -r <<<"${latest_msi_json_data}" .location)
#latest_msi_size=$(jq -r <<<"${latest_msi_json_data}" .sizeInBytes)

###########################

if ! ( xmlstarlet select \
    --text \
    --template \
    --match "//_:script[not(@src)]" \
    --value-of 'text()' \
    --nl \
    --output "##################################################" \
    --nl \
    "${start_page}" \
    > "${start_page_matching_scripts}"
)
then
  error "Unable to extract script blocks from \"${start_page}\". Default xmlns problem again?"
fi

script_count=$(grep -c '^##*$' "${start_page_matching_scripts}")
case "${script_count}" in
  1|2) : ;;
  *)
    error "Page changed again. Check \"${start_page_matching_scripts}\" and \"${start_page}\""
    ;;
esac

csplit \
    --prefix="${start_page_script_prefix}" \
    --suffix-format="${start_page_script_suffix}" \
    --keep-files \
    --suppress-matched \
    --quiet \
    -- \
    "${start_page_matching_scripts}" \
    '/^##*$/' '{*}'

for start_page_js in ${start_page_script_prefix}.*.js NO_MATCHES
do
  if [ "${start_page_js}" = NO_MATCHES ]
  then
    error "No matches in ${start_page_script_prefix}.*.js"
  fi
  if grep -q -E '\bwindow\.__NUXT__\b' -- "${start_page_js}"
  then
    break
  fi
done

node - > "${start_page_json}" <<EOF
var vm = require("vm");
var fs = require("fs");
var data = fs.readFileSync('${start_page_js}');
const script = new vm.Script(data);

var window = {};
script.runInThisContext();
process.stdout.write(JSON.stringify(window.__NUXT__.data));
EOF

cat "${start_page_json}" \
| jq -S '
[
  .[0].majorReleases[]
  |select(.channelId=="stable")
]
|sort_by(.majorVersion|tonumber)
[-1]
.releases
|sort_by(.fullVersion|split(".")|map(tonumber))
[-1]
|del(
  .platforms[]
  |select(.platformId!="windows-x64")
)
' > "${latest_json}"

latest_version=$(cat "${latest_json}" | jq -r .fullVersion)
latest_msi_json_data=$(cat "${latest_json}" | jq -c '.platforms[0]')
#latest_msi_hash=$(jq -r <<<"${latest_msi_json_data}" .hash)
#latest_msi_hashalgo=$(jq -r <<<"${latest_msi_json_data}" .hashAlgorithm)
latest_msi_url=$(jq -r <<<"${latest_msi_json_data}" '.downloadUrl')
latest_msi_size=$(jq -r <<<"${latest_msi_json_data}" '.sizeInBytes')

latest_msi_hashalgo=SKIP

###########################

latest_msi_name=${latest_msi_url##*/}
if [ "${latest_msi_name}" != MicrosoftEdgeEnterpriseX64.msi ]
then
  error 'unexpected filename in MSI URL:' "${latest_msi_url}"
fi
latest_msi_name=${latest_msi_name%.msi}
latest_msi_dl=${latest_msi_name}.${latest_version}.msi

if [ "${latest_msi_hashalgo}" != SKIP ]
then
  case "${latest_msi_hashalgo,,}" in
  sha256) : ;;
  *) error 'unexpected hash algorithm:' "${latest_msi_hashalgo}" ;;
  esac
  latest_msi_cksum_prog=${latest_msi_hashalgo,,}sum
  latest_msi_cksum_txt=${latest_msi_name}.${latest_version}.${latest_msi_cksum_prog}.txt
  cat > "${latest_msi_cksum_txt}" <<EOF
${latest_msi_hash,,}  ${latest_msi_dl}
EOF
fi
if [ ! -f "${latest_msi_dl}" ]
then
  curl -gLRo "${latest_msi_dl}" "${latest_msi_url}"
fi
if [ "${latest_msi_hashalgo}" != SKIP ]
then
  "${latest_msi_cksum_prog}" -c "${latest_msi_cksum_txt}"
fi
ls -lF -- "${latest_msi_dl}"

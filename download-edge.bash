#!/usr/bin/env bash
# vim: shiftwidth=2 tabstop=2 expandtab
set -euo pipefail
[[ "${TRACE-0}" == "1" ]] && set -x

msi_download_fwlink='https://go.microsoft.com/fwlink/?LinkID=2093437'
msi_download_filename='MicrosoftEdgeEnterpriseX64'
msi_download_fileext='.msi'
msi_download_file=${msi_download_filename}${msi_download_fileext}


error () {
  printf >&2 ERROR:
  printf >&2 ' %s' "$@"
  printf >&2 '\n'
  exit 1
}


cd -- "$(dirname -- "$BASH_SOURCE")/../downloads"

curl_args=(
    --silent
    --location
    --remote-time
    --output "${msi_download_file}"
)
if [ -e "${msi_download_file}" ]
then
  curl_args+=( --time-cond "${msi_download_file}" )
  prev_cksum=$(sha256sum -- "${msi_download_file}")
else
  prev_cksum=''
fi
curl "${curl_args[@]}" "${msi_download_fwlink}"
cksum=$(sha256sum -- "${msi_download_file}")
if [ "${prev_cksum}" = "${cksum}" ]
then
  : No change
  exit 0
fi

mime_type=$(file --brief --mime-type -- "${msi_download_file}")
if [ "${mime_type}" != application/x-msi ]
then
  error 'unexpected mime type:' "${mime_type}"
fi

metadata=$(file --brief -- "${msi_download_file}")
get_value_from_metadata () {
  if ! grep --only-matching --perl-regexp --regexp="(?<=\\b${1}: )[^,]+" <<<"${metadata}"
  then
    error "did not find tag \"$1\" in metadata:" "${metadata}"
  fi
}
expected_subject='Microsoft Edge Installer'
actual_subject=$(get_value_from_metadata Subject)
if [ "${expected_subject}" != "${actual_subject}" ]
then
  error "expected subject \"${expected_subject}\", saw \"${actual_subject}\" in metadata:" "${metadata}"
fi
comments=$(get_value_from_metadata Comments)
edge_version=${comments%% Copyright *}
if [ "${comments}" = "${edge_version}" ]
then
  error "expected comments like \"VERSION Copyright YYYY Microsoft ...\", saw \"${comments}\" in metadata:" "${metadata}"
fi
if [[ ! "${edge_version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]
then
  error 'unexpected version from metadata:' "${edge_version}"
fi
versioned_file=${msi_download_filename}.${edge_version}${msi_download_fileext}
if [ -e "${versioned_file}" ]
then
  error 'versioned file already exists:' "${versioned_file}"
fi
ln --no-target-directory -- "${msi_download_file}" "${versioned_file}"
ls -lF -- "${versioned_file}"

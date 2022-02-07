base=$(cd -- "$(dirname -- "$BASH_SOURCE")" && /bin/pwd)
downloads=$base/downloads
updates=$base/updates

wsusoffline_base_url=https://gitlab.com/wsusoffline/wsusoffline
wsusoffline_release_tag=12.6.1_CommunityEdition
wsusoffline_release_name=wsusofflineCE1261hf1
wsusoffline_zip_gitlabdiskhash=9c12b49c6798155ee71c56e2b972d000
wsusoffline_hashes_gitlabdiskhash=af62cb5f18760936f5396e279dd698e1
wsusoffline_uploads_url=$wsusoffline_base_url/uploads
wsusoffline_release_url=$wsusoffline_base_url/-/releases/$wsusoffline_release_tag
wsusoffline_zip_file=$wsusoffline_release_name.zip
wsusoffline_zip_url=$wsusoffline_uploads_url/$wsusoffline_zip_gitlabdiskhash/$wsusoffline_zip_file
wsusoffline_hashes_file=${wsusoffline_release_name}_hashes.txt
wsusoffline_hashes_url=$wsusoffline_uploads_url/$wsusoffline_hashes_gitlabdiskhash/$wsusoffline_hashes_file

here=$(cd -- "$(dirname -- "$BASH_SOURCE")" && /bin/pwd)
files=$here/files

base=$(cd -- "$here/.." && /bin/pwd)
downloads=$base/downloads
updates=$base/updates

## WSUS Offline
wsusoffline_prune_days=120
# settings that change with each release
wsusoffline_release_tag=12.6.1_CommunityEdition
wsusoffline_release_name=wsusofflineCE1261hf1
wsusoffline_zip_gitlabdiskhash=9c12b49c6798155ee71c56e2b972d000
wsusoffline_hashes_gitlabdiskhash=af62cb5f18760936f5396e279dd698e1
# settings that should not change with each release
wsusoffline_base_url=https://gitlab.com/wsusoffline/wsusoffline
wsusoffline_uploads_url=$wsusoffline_base_url/uploads
wsusoffline_release_url=$wsusoffline_base_url/-/releases/$wsusoffline_release_tag
wsusoffline_zip_file=$wsusoffline_release_name.zip
wsusoffline_zip_url=$wsusoffline_uploads_url/$wsusoffline_zip_gitlabdiskhash/$wsusoffline_zip_file
wsusoffline_hashes_file=${wsusoffline_release_name}_hashes.txt
wsusoffline_hashes_url=$wsusoffline_uploads_url/$wsusoffline_hashes_gitlabdiskhash/$wsusoffline_hashes_file

## Microsoft updates that should not be copied to DVD
kb_prune_days=120
kb_ignores=(

    ## Patch Tuesday  08 Feb 2022
    # need: 5010345  # Windows 10 Version 1909 for x64-based Systems
    5010342  # Windows 10 Version 20H2 for x64-based Systems
    5010342  # Windows 10 Version 21H1 for x64-based Systems
    5010342  # Windows 10 Version 21H2 for x64-based Systems
    5010351  # Windows 10 Version 1809 for x64-based Systems
    5010358  # Windows 10 for x64-based Systems
    5010354  # Windows Windows Server 2022
    5010359  # Windows 10 Version 1607 for x64-based Systems
    5010386  # Windows 11 for x64-based Systems

    ## Patch Tuesday  11 Jan 2022
    # need: 5009545  # Windows 10 Version 1909 for x64-based Systems
    5009543  # Windows 10 Version 20H2 for x64-based Systems
    5009543  # Windows 10 Version 21H1 for x64-based Systems
    5009543  # Windows 10 Version 21H2 for x64-based Systems
    5009546  # Windows 10 Version 1607 for x64-based Systems
    5009557  # Windows 10 Version 1809 for x64-based Systems
    5009566  # Windows 11 for x64-based Systems
    5009585  # Windows 10 for x64-based Systems

    ## Patch Tuesday  14 Dec 2021
    # need: 5008206  # Windows 10 Version 1909 for x64-based Systems
    5008207  # Windows 10 Version 1607 for x64-based Systems
    5008212  # Windows 10 Version 2004 for x64-based Systems
    5008212  # Windows 10 Version 20H2 for x64-based Systems
    5008212  # Windows 10 Version 21H1 for x64-based Systems
    5008212  # Windows 10 Version 21H2 for x64-based Systems
    5008215  # Windows 11 for x64-based Systems
    5008218  # Windows 10 Version 1809 for x64-based Systems
    5008230  # Windows 10 for x64-based Systems

)
# unique-ify KB numbers
kb_ignores=( $(printf '%s\n' "${kb_ignores[@]}" | sort -u) )

## Rhino3D 7
rhino7_release_date='20220208'
rhino7_version_full='7.15.22039.13001'
rhino7_installer_sha256='315d0a7704a22fbff50026e5533d7aa9f8400bd0515b1cbad80eae893ea63a9c'
rhino7_installer_file=rhino_en-us_$rhino7_version_full.exe
rhino7_installer_url="https://files.mcneel.com/dujour/exe/$rhino7_release_date/$rhino7_installer_file"
rhino7_release_notification_url='https://discourse.mcneel.com/t/rhino-7-service-release-available/114088'
rhino7_download_latest_url='https://www.rhino3d.com/download/rhino/latest'

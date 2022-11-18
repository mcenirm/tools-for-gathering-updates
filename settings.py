"""Settings that should be change controlled"""

from pathlib import Path

from credentials import *
from local_settings import *

here = Path(__file__).parent

files = here / "files"

base = here.parent
clones = base / "clones"
downloads = base / "downloads"
updates = base / "updates"
dvds = base / "dvds"

## WSUS Offline
wsusoffline_prune_days = 120
wsusoffline_updates_dir = updates / "wsusoffline"
wsusoffline_client_dir = wsusoffline_updates_dir / "client"
# settings that change with each release
wsusoffline_release_tag = "12.6.1_CommunityEdition"
wsusoffline_release_name = "wsusofflineCE1261hf1"
wsusoffline_zip_gitlabdiskhash = "9c12b49c6798155ee71c56e2b972d000"
wsusoffline_hashes_gitlabdiskhash = "af62cb5f18760936f5396e279dd698e1"
# settings that should not change with each release
wsusoffline_base_url = "https://gitlab.com/wsusoffline/wsusoffline"
wsusoffline_uploads_url = f"{wsusoffline_base_url}/uploads"
wsusoffline_release_url = f"{wsusoffline_base_url}/-/releases/{wsusoffline_release_tag}"
wsusoffline_zip_file = f"{wsusoffline_release_name}.zip"
wsusoffline_zip_url = (
    f"{wsusoffline_uploads_url}/{wsusoffline_zip_gitlabdiskhash}/{wsusoffline_zip_file}"
)
wsusoffline_hashes_file = f"{wsusoffline_release_name}_hashes.txt"
wsusoffline_hashes_url = "/".join(
    (
        wsusoffline_uploads_url,
        wsusoffline_hashes_gitlabdiskhash,
        wsusoffline_hashes_file,
    )
)
wsusoffline_git_url = f"{wsusoffline_base_url}.git"

## Microsoft updates that should not be copied to DVD
kb_ignores = {
    ## Patch Tuesday  08 Feb 2022
    "5010345",  # Windows 10 Version 1909 for x64-based Systems
    # need: 5010342  # Windows 10 Version 20H2 for x64-based Systems
    # need: 5010342  # Windows 10 Version 21H1 for x64-based Systems
    # need: 5010342  # Windows 10 Version 21H2 for x64-based Systems
    "5010351",  # Windows 10 Version 1809 for x64-based Systems
    "5010358",  # Windows 10 for x64-based Systems
    "5010354",  # Windows Windows Server 2022
    "5010359",  # Windows 10 Version 1607 for x64-based Systems
    "5010386",  # Windows 11 for x64-based Systems
    ## Patch Tuesday  11 Jan 2022
    "5009545",  # Windows 10 Version 1909 for x64-based Systems
    # need: 5009543  # Windows 10 Version 20H2 for x64-based Systems
    # need: 5009543  # Windows 10 Version 21H1 for x64-based Systems
    # need: 5009543  # Windows 10 Version 21H2 for x64-based Systems
    "5009546",  # Windows 10 Version 1607 for x64-based Systems
    "5009557",  # Windows 10 Version 1809 for x64-based Systems
    "5009566",  # Windows 11 for x64-based Systems
    "5009585",  # Windows 10 for x64-based Systems
    ## Patch Tuesday  14 Dec 2021
    "5008206",  # Windows 10 Version 1909 for x64-based Systems
    "5008207",  # Windows 10 Version 1607 for x64-based Systems
    # need: 5008212  # Windows 10 Version 2004 for x64-based Systems
    # need: 5008212  # Windows 10 Version 20H2 for x64-based Systems
    # need: 5008212  # Windows 10 Version 21H1 for x64-based Systems
    # need: 5008212  # Windows 10 Version 21H2 for x64-based Systems
    "5008215",  # Windows 11 for x64-based Systems
    "5008218",  # Windows 10 Version 1809 for x64-based Systems
    "5008230",  # Windows 10 for x64-based Systems
}

## Rhino3D 7
rhino7_release_date = "20221104"
rhino7_version_full = "7.24.22308.15001"
rhino7_installer_sha256 = (
    "3afb9c0f5257de0411eec9d9b485da1f512fb449dc642e3e5eac50258e83e59f"
)
rhino7_installer_file = f"rhino_en-us_{rhino7_version_full}.exe"
rhino7_installer_url = (
    f"https://files.mcneel.com/dujour/exe/{rhino7_release_date}/{rhino7_installer_file}"
)
rhino7_release_notification_url = (
    "https://discourse.mcneel.com/t/rhino-7-service-release-available/114088"
)
rhino7_download_latest_url = "https://www.rhino3d.com/download/rhino/latest"
rhino7_download_latest_windows_confirmation_url = (
    "https://www.rhino3d.com/download/rhino-for-windows/7/latest"
)

# TODO POST to https://www.rhino3d.com/download/rhino/latest to get direct download url
#  * email:           ...       (url encoded: example%40example.com)
#  * direction_next:  "Next >"  (url encoded: Next+%3E)
#  * current_page:    license_info

## Nessus
nessus_updates_dir = updates / "nessus"
nessus_plugin_dir_prefix = "nessus-plugin-set-"
nessus_plugin_details_file = (
    nessus_updates_dir / f"{nessus_plugin_dir_prefix}details.bash"
)
#
nessus_plugin_file_name = "all-2.0.tar.gz"
nessus_plugin_url = f"https://plugins.nessus.org/v2/nessus.php?f={nessus_plugin_file_name}&u={nessus_plugin_u}&p={nessus_plugin_p}"
nessus_plugin_version_url = "https://plugins.nessus.org/v2/plugins.php"
nessus_installer_listing_url = (
    "https://www.tenable.com/downloads/nessus?loginAttempted=true"
)

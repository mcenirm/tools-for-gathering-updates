"""Use WSUS Offline to download updates from Microsoft"""


from subprocess import check_call

import settings

CWD = settings.wsusoffline_updates_dir / "sh"

# TODO
# Add option to force updates for some or all categories,
# even if done recently (see "sh/libraries/timestamps.bash")
#  * remove timestamps/timestamp*.txt
#  * (UNTESTED) remove client/md/hashes*.txt to avoid warnings about integrity database

check_call(
    [
        "./download-updates.bash",
        "w100-x64",
        "enu",
        "-includesp",
        "-includecpp",
        "-includedotnet",
        "-includewddefs",
    ],
    cwd=CWD,
)

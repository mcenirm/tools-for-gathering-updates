"""Use WSUS Offline to download updates from Microsoft"""

import subprocess
import sys

import helpers
import settings

options_message = """Options:
    --force    ignore timestamps
"""
ignore_timestamps = False
args = sys.argv[1:]
while args:
    match args[0]:
        case "--force":
            ignore_timestamps = True
            args.pop(0)
        case _:
            print(options_message, file=sys.stderr)
            sys.exit(1)

CWD = settings.wsusoffline_updates_dir / "sh"

# TODO
# Add option to force updates for some or all categories,
# even if done recently (see "sh/libraries/timestamps.bash")
#  * remove timestamps/timestamp*.txt
#  * (UNTESTED) remove client/md/hashes*.txt to avoid warnings about integrity database

if ignore_timestamps:
    helpers.rm_v(
        globs=("timestamp*.txt",),
        base_directory=settings.wsusoffline_updates_dir / "timestamps",
    )

subprocess.run(
    [
        "./download-updates.bash",
        "w100-x64",
        "enu",
        "-includesp",
        "-includecpp",
        "-includedotnet",
        "-includewddefs",
    ],
    check=True,
    cwd=CWD,
)

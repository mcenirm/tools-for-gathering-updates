"""Install WSUS Offline"""

import pathlib
import shlex
import shutil
import subprocess

import helpers
import settings

helpers.ensure_directory(settings.updates)
CWD = settings.updates / "wsusoffline" / "sh"

helpers.unzip(
    settings.downloads / settings.wsusoffline_zip_file,
    destination_directory=settings.updates,
)

# avoid pinging external system
# TODO avoid pinging at all
# TODO use python standard library instead of external sed
subprocess.run(
    [
        "sed",
        "-i",
        "-e",
        "s/ www.wsusoffline.net / localhost /",
        "common-tasks/40-configure-downloaders.bash",
    ],
    check=True,
    cwd=CWD,
)

for dst, names in {
    "": [
        "update-generator.ini",
        "windows-10-versions.ini",
    ],
    "../client/static/custom": [
        "StaticUpdateIds-servicing-w100-19042.txt",
        "StaticUpdateIds-servicing-w100-19043.txt",
        "StaticUpdateIds-servicing-w100-19044.txt",
    ],
}.items():
    dst = CWD / dst
    assert dst.is_dir()
    for name in names:
        src = settings.files / "files-for-wsusoffline" / name
        newpath = shutil.copy2(src=src, dst=dst)
        print(shlex.quote(str(src)), "->", shlex.quote(str(newpath)))

subprocess.run(["bash", "fix-file-permissions.bash"], check=True, cwd=CWD)

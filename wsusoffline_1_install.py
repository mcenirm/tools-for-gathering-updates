"""Install WSUS Offline"""

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

subprocess.run(["bash", "fix-file-permissions.bash"], check=True, cwd=CWD)

for n in ["update-generator.ini", "windows-10-versions.ini"]:
    # TODO use python standard library instead of external cp
    subprocess.run(
        ["cp", "-ipv", f"{settings.files}/wsusoffline-{n}", f"./{n}"],
        check=True,
        cwd=CWD,
    )

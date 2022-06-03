"""Remove unnecessary files from WSUS Offline client directory"""

import datetime
import functools

import helpers
import settings

# remove update files for KB numbers that we ignore
# (eg, due to wrong Windows 10 version not being filtered out)
helpers.rm_v(
    globs=(f"w100-x64/glb/*-kb{kb}-*.cab" for kb in settings.kb_ignores),
    base_directory=settings.wsusoffline_client_dir,
)


# remove other update files that are known to be unneeded
# (mostly 32-bit files when 64-bit options also exist)
others = (
    "cpp/vcredist*_x86.exe",
    "dotnet/aspnetcore-runtime-*-win-x86.exe",
    "dotnet/dotnet-runtime-*-win-x86.exe",
    "dotnet/windowsdesktop-runtime-*-win-x86.exe",
    "msedge/MicrosoftEdgeUpdateSetup_X86_*.exe",
    "msedge/MicrosoftEdge_X86_*.exe",
)
helpers.rm_v(globs=others, base_directory=settings.wsusoffline_client_dir)


# remove any update files that are old enough
# that they should have been applied already
paths_to_check = (
    "cpp",
    "dotnet",
    "msedge",
    "w100-x64/glb",
)


prune_expiry = datetime.datetime.now() - datetime.timedelta(
    days=settings.wsusoffline_prune_days
)
file_is_too_old = functools.partial(helpers.file_is_older_than, expiry=prune_expiry)
for base_directory in (settings.wsusoffline_client_dir / _ for _ in paths_to_check):
    helpers.rm_v(
        rglobs=("*.cab", "*.exe", "*.msu"),
        base_directory=base_directory,
        only_if=file_is_too_old,
    )

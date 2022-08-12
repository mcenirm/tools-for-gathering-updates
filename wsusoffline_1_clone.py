"""Install WSUS Offline"""

import kits.helpers as helpers
import settings

helpers.ensure_directory(settings.clones)
print(
    helpers.git_clone(
        settings.wsusoffline_git_url,
        work_dir=settings.clones / "wsusoffline",
    )
)

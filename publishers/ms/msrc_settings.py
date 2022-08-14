from __future__ import annotations

import datetime

MSRC_API_DOWNLOAD_AGE_THRESHOLD = datetime.timedelta(hours=12)
MSRC_API_RELEASE_AGE_THRESHOLD = datetime.timedelta(days=365 // 2)
MSRC_API_UPDATE_DOWNLOAD_FMT = "msrc-update.{id_}.cvrf.xml"
MSRC_API_UPDATES_DOWNLOAD_STRFTIME = "msrc-updates.%Y.json"
MSRC_API_UPDATES_URL_STRFTIME = "https://api.msrc.microsoft.com/cvrf/v2.0/Updates('%Y')"

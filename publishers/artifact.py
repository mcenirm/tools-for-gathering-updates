from __future__ import annotations

from dataclasses import dataclass, field

from .component import Component


@dataclass(kw_only=True, frozen=True)
class DownloadArtifact:
    url: str


@dataclass(kw_only=True, frozen=True)
class ArtifactContainer:
    moniker: str
    downloads: list[DownloadArtifact] = field(default_factory=list)


class ComponentWithDownloadArtifacts(Component):
    def __init__(self, *args, downloads_moniker: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.container = ArtifactContainer(moniker=downloads_moniker)

    def add_download(self, url: str) -> DownloadArtifact:
        a = DownloadArtifact(url=url)
        self.container.downloads.append(a)
        return a

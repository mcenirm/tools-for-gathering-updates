from __future__ import annotations

import pathlib
import typing
from html.parser import HTMLParser

from icecream import ic
from publishers import ComponentWithDownloadArtifacts, UpdateStatus

from .edge_settings import EDGE_FOR_BUSINESS_MONIKER, EDGE_FOR_BUSINESS_START_URL


class MicrosoftEdge(ComponentWithDownloadArtifacts):
    def __init__(
        self,
        *args,
        downloads_moniker=EDGE_FOR_BUSINESS_MONIKER,
        start_url=EDGE_FOR_BUSINESS_START_URL,
        **kwargs,
    ) -> None:
        super().__init__(*args, downloads_moniker=downloads_moniker, **kwargs)
        self.start_url = start_url
        self.start = self.add_download(url=start_url)

    def check_for_updates(self) -> UpdateStatus:
        dlstatus = self.download(self.start)
        if dlstatus.should_process():
            commercian_json_data = extract_commercial_json_data(dlstatus.path())
            ...
        return super().check_for_updates()


class ExtractCommercialJsonDataParser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.commercial_json_data = None

    def handle_charref(self, name: str) -> None:
        return super().handle_charref(name)

    def handle_comment(self, data: str) -> None:
        return super().handle_comment(data)

    def handle_data(self, data: str) -> None:
        return super().handle_data(data)

    def handle_decl(self, decl: str) -> None:
        return super().handle_decl(decl)

    def handle_endtag(self, tag: str) -> None:
        return super().handle_endtag(tag)

    def handle_entityref(self, name: str) -> None:
        return super().handle_entityref(name)

    def handle_endtag(self, tag: str) -> None:
        return super().handle_endtag(tag)

    def handle_pi(self, data: str) -> None:
        return super().handle_pi(data)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        return super().handle_startendtag(tag, attrs)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if attrs:
            ic(attrs)
            raise NotImplementedError("TODO")
        return super().handle_starttag(tag, attrs)


def extract_commercial_json_data(p: pathlib.Path) -> typing.Any:
    parser = ExtractCommercialJsonDataParser()
    with p.open() as f:
        parser.feed(f.read())
    return parser.commercial_json_data

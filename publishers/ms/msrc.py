from __future__ import annotations

import dataclasses
import datetime
import json
import pathlib
import typing
import xml.etree.ElementTree as ET

import kits.cvrf as cvrf
import kits.helpers as helpers
import settings
from icecream import ic
from rich import inspect as ri

from .msrc_settings import (
    MSRC_API_DOWNLOAD_AGE_THRESHOLD,
    MSRC_API_RELEASE_AGE_THRESHOLD,
    MSRC_API_UPDATE_DOWNLOAD_FMT,
    MSRC_API_UPDATES_DOWNLOAD_STRFTIME,
    MSRC_API_UPDATES_URL_STRFTIME,
)


@dataclasses.dataclass(kw_only=True, frozen=True)
class MsrcCvrfCitation:
    alias: str
    current_release_date: datetime.datetime
    cvrf_url: str
    document_title: str
    id_: str
    initial_release_date: datetime.datetime
    severity: str | None

    @classmethod
    def from_dict(cls, d: dict) -> MsrcCvrfCitation:
        return MsrcCvrfCitation(
            alias=d["Alias"],
            current_release_date=helpers.parse_isoz_datetime(d["CurrentReleaseDate"]),
            cvrf_url=d["CvrfUrl"],
            document_title=d["DocumentTitle"],
            id_=d["ID"],
            initial_release_date=helpers.parse_isoz_datetime(d["InitialReleaseDate"]),
            severity=d["Severity"],
        )

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


def _is_missing_or_not_too_recent(p: pathlib.Path) -> bool:
    if not p.exists():
        return True
    if helpers.file_is_older_than(
        p, datetime.datetime.now() - MSRC_API_DOWNLOAD_AGE_THRESHOLD
    ):
        return True
    return False


def download_year_listing(
    year_representative: int | datetime.date | datetime.datetime,
) -> pathlib.Path:
    if isinstance(year_representative, int):
        year_representative = datetime.date(year_representative, 1, 1)
    url = year_representative.strftime(MSRC_API_UPDATES_URL_STRFTIME)
    dlpath = settings.downloads / year_representative.strftime(
        MSRC_API_UPDATES_DOWNLOAD_STRFTIME
    )
    if _is_missing_or_not_too_recent(dlpath):
        dlpath = helpers.curl(url, downloaded_file_path=dlpath)
    return dlpath


def download_update_metadata(citation: MsrcCvrfCitation) -> pathlib.Path:
    dlpath = settings.downloads / MSRC_API_UPDATE_DOWNLOAD_FMT.format_map(
        citation.asdict()
    )
    if _is_missing_or_not_too_recent(dlpath):
        dlpath = helpers.curl(citation.cvrf_url, downloaded_file_path=dlpath)
    return dlpath


def download_updates_metadata() -> list[pathlib.Path]:
    update_metadata_paths = []
    downloaded_year_listings: list[pathlib.Path] = []
    now = datetime.datetime.now(datetime.timezone.utc)
    ignore_releases_before = now - MSRC_API_RELEASE_AGE_THRESHOLD
    for year in sorted(set((range(ignore_releases_before.year, now.year + 1)))):
        downloaded_year_listings.append(download_year_listing(year))
    for downloaded_year_listing_path in downloaded_year_listings:
        with downloaded_year_listing_path.open() as f:
            data = json.load(f)
        for citation_data in data["value"]:
            citation = MsrcCvrfCitation.from_dict(citation_data)
            if citation.current_release_date > ignore_releases_before:
                update_metadata_paths.append(
                    download_update_metadata(citation=citation)
                )
    return update_metadata_paths


def cvrf_get_full_product_names(
    *,
    cvrf_doc: ET.Element,
    branch_chain: list[Branch] = [],
) -> typing.Generator[FullProductName, None, None]:
    # TODO confirm that cvrfdoc never has more than one ProductTree
    product_tree = cvrf_doc.find(
        CvrfProdNS.ProductTree,
        namespaces=CVRF_XMLNS_MAP,
    )
    epath = [product_tree]
    for link in branch_chain:
        for branch in epath[-1].iterfind(
            CvrfProdNS.Branch,
            namespaces=CVRF_XMLNS_MAP,
        ):
            n, t = branch.get("Name"), branch.get("Type")
            if t == link.type and n == link.name:
                epath.append(branch)
                break
            raise IndexError("Missing branch link", link)
    for product_elem in epath[-1].iterfind(
        CvrfProdNS.FullProductName,
        namespaces=CVRF_XMLNS_MAP,
    ):
        product = FullProductName(
            full_product_name=product_elem.text,
            product_id=product_elem.get("ProductID"),
            branch_chain=epath[1:],
        )
        yield product


def cvrf_get_product_id(
    *,
    cvrf_doc: ET.Element,
    branch_chain: list[Branch],
    full_product_name: str,
) -> str | None:
    for product in cvrf_find_products(
        cvrf_doc=cvrf_doc,
        branch_chain=branch_chain,
        full_product_name=None,
    ):
        if full_product_name == product.full_product_name:
            return product.product_id
    return None


def gloam(tag: str, value: str, indent_level: int = 0, /) -> None:
    short_tag = tag.split("}")[-1]
    label = f"""{"  " * indent_level}{short_tag}:"""
    msg = f"{label:24} {value}"
    print(msg)


if __name__ == "__main__":
    # microsoft_branch = Branch.vendor("Microsoft")
    # windows_branch = Branch.family("Windows")
    update_metadata_paths = download_updates_metadata()
    for ump in update_metadata_paths:
        tree = ET.parse(str(ump))
        # parent_map = {c: p for p in tree.iter() for c in p}
        cvrfdoc = cvrf.load_from_etree(tree=tree)
        watching_product_ids = {
            fpn.product_id
            for fpn in cvrf_get_full_product_names(
                cvrf_doc=root,
                branch_chain=[microsoft_branch, windows_branch],
            )
            if fpn.full_product_name == "Windows 10 Version 21H2 for x64-based Systems"
        }
        ic(watching_product_ids)
        # for p in cvrf_find_products(
        #     cvrf_doc=root, branch_chain=[], full_product_name=None
        # ):
        #     ic(p)
        break

from __future__ import annotations

import dataclasses
import datetime
import json
import pathlib
import typing
import xml.etree.ElementTree as ET

import kits.helpers as helpers
import settings
from icecream import ic
from kits.cvrf import (
    CVRF_PROD_ATTR_NAME,
    CVRF_PROD_ATTR_PRODUCT_ID,
    CVRF_PROD_ATTR_TYPE,
    CvrfNS,
    CvrfProdNS,
    CvrfVulnNS,
    Revision,
)
from kits.xml import ElementTreeParentMap as ParentMap
from kits.xml import short_tag
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
    label = f"""{"  " * indent_level}{short_tag(tag)}:"""
    msg = f"{label:24} {value}"
    print(msg)


if __name__ == "__main__":
    # microsoft_branch = Branch.vendor("Microsoft")
    # windows_branch = Branch.family("Windows")
    update_metadata_paths = download_updates_metadata()
    for ump in update_metadata_paths:
        tree = ET.parse(str(ump))
        parent_map = ParentMap(tree)
        # cvrfdoc = cvrf.load_from_etree(tree=tree)
        # watching_product_ids = {
        #     fpn.product_id
        #     for fpn in cvrf_get_full_product_names(
        #         cvrf_doc=root,
        #         branch_chain=[microsoft_branch, windows_branch],
        #     )
        #     if fpn.full_product_name == "Windows 10 Version 21H2 for x64-based Systems"
        # }
        # ic(watching_product_ids)
        # for p in cvrf_find_products(
        #     cvrf_doc=root, branch_chain=[], full_product_name=None
        # ):
        #     ic(p)
        # break
        cutoff = 10
        for i, e in enumerate(tree.iter()):
            match e.tag:
                case CvrfNS.cvrfdoc:
                    ...
                case CvrfNS.Alias:
                    ...
                case CvrfNS.ContactDetails:
                    ...
                case CvrfNS.CurrentReleaseDate:
                    ...
                case CvrfNS.Date:
                    ...
                    # gloam(e.tag, e.text, 1)
                    # for i, p in enumerate(parent_map.ancestors(e)):
                    #     if p.tag != CvrfNS.cvrfdoc:
                    #         gloam(p.tag, str([short_tag(c.tag) for c in p]), i + 1)
                case CvrfNS.Description:
                    ...
                    # gloam(e.tag, e.text, 1)
                case CvrfNS.DocumentNotes:
                    ...
                case CvrfNS.DocumentPublisher:
                    ...
                case CvrfNS.DocumentTitle:
                    print(e.text)
                case CvrfNS.DocumentTracking:
                    ...
                case CvrfNS.DocumentType:
                    ...
                case CvrfNS.ID:
                    ...
                case CvrfNS.Identification:
                    ...
                case CvrfNS.InitialReleaseDate:
                    ...
                case CvrfNS.IssuingAuthority:
                    ...
                case CvrfNS.Note:
                    ...
                case CvrfNS.Number:
                    ...
                    # gloam(e.tag, e.text, 1)
                case CvrfNS.Revision:
                    print(Revision.from_etree(e))
                    # gloam(e.tag, "")
                case CvrfNS.RevisionHistory:
                    ...
                case CvrfNS.Status:
                    ...
                case CvrfNS.Version:
                    ...
                case CvrfProdNS.Branch:
                    ...
                case CvrfProdNS.FullProductName:
                    if all([s in e.text for s in ["Windows 10", "21H2", "x64"]]):
                        pid = e.get(CVRF_PROD_ATTR_PRODUCT_ID)
                        branches = [
                            p
                            for p in parent_map.ancestors(e)
                            if p.tag == CvrfProdNS.Branch
                        ]
                        branches.reverse()
                        branch_path = [
                            " = ".join(
                                [
                                    b.get(CVRF_PROD_ATTR_TYPE) or "??",
                                    repr(b.get(CVRF_PROD_ATTR_NAME)),
                                ]
                            )
                            for b in branches
                        ]
                        print(pid, "(" + " > ".join(branch_path) + ")", repr(e.text))
                        cutoff -= 1
                case CvrfProdNS.ProductTree:
                    ...
                case CvrfVulnNS.Acknowledgment:
                    ...
                case CvrfVulnNS.Acknowledgments:
                    ...
                case CvrfVulnNS.AffectedFiles:
                    ...
                case CvrfVulnNS.BaseScore:
                    ...
                case CvrfVulnNS.CVE:
                    ...
                case CvrfVulnNS.CVSSScoreSets:
                    ...
                case CvrfVulnNS.Description:
                    ...
                case CvrfVulnNS.FixedBuild:
                    ...
                case CvrfVulnNS.Name:
                    ...
                case CvrfVulnNS.Note:
                    ...
                case CvrfVulnNS.Notes:
                    ...
                case CvrfVulnNS.ProductID:
                    ...
                case CvrfVulnNS.ProductStatuses:
                    ...
                case CvrfVulnNS.Remediation:
                    ...
                case CvrfVulnNS.Remediations:
                    ...
                case CvrfVulnNS.RestartRequired:
                    ...
                case CvrfVulnNS.Revision:
                    ...
                case CvrfVulnNS.RevisionHistory:
                    ...
                case CvrfVulnNS.ScoreSet:
                    ...
                case CvrfVulnNS.Status:
                    ...
                case CvrfVulnNS.SubType:
                    ...
                case CvrfVulnNS.Supercedence:
                    ...
                case CvrfVulnNS.TemporalScore:
                    ...
                case CvrfVulnNS.Threat:
                    ...
                case CvrfVulnNS.Threats:
                    ...
                case CvrfVulnNS.Title:
                    ...
                case CvrfVulnNS.URL:
                    ...
                case CvrfVulnNS.Vector:
                    ...
                case CvrfVulnNS.Vulnerability:
                    ...

                case _:
                    ic(e.tag)
                    cutoff -= 1
            if cutoff < 1:
                break
        break

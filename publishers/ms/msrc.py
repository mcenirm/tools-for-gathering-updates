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
from rich import inspect as ri

from .msrc_settings import (
    MSRC_API_DOWNLOAD_AGE_THRESHOLD,
    MSRC_API_RELEASE_AGE_THRESHOLD,
    MSRC_API_UPDATE_DOWNLOAD_FMT,
    MSRC_API_UPDATES_DOWNLOAD_STRFTIME,
    MSRC_API_UPDATES_URL_STRFTIME,
)


@helpers.xmlns(uri="http://www.icasi.org/CVRF/schema/cvrf/1.1")
class CvrfNS:
    cvrfdoc: str
    Alias: str
    ContactDetails: str
    CurrentReleaseDate: str
    Date: str
    Description: str
    DocumentNotes: str
    DocumentPublisher: str
    DocumentTitle: str
    DocumentTracking: str
    DocumentType: str
    ID: str
    Identification: str
    InitialReleaseDate: str
    IssuingAuthority: str
    Note: str
    Number: str
    Revision: str
    RevisionHistory: str
    Status: str
    Version: str


@helpers.xmlns(uri="http://www.icasi.org/CVRF/schema/prod/1.1")
class CvrfProdNS:
    Branch: str
    FullProductName: str
    ProductTree: str


@helpers.xmlns(uri="http://www.icasi.org/CVRF/schema/vuln/1.1")
class CvrfVulnNS:
    Acknowledgment: str
    Acknowledgments: str
    AffectedFiles: str
    BaseScore: str
    CVE: str
    CVSSScoreSets: str
    Description: str
    FixedBuild: str
    Name: str
    Note: str
    Notes: str
    ProductID: str
    ProductStatuses: str
    Remediation: str
    Remediations: str
    RestartRequired: str
    Revision: str
    RevisionHistory: str
    ScoreSet: str
    Status: str
    SubType: str
    Supercedence: str
    TemporalScore: str
    Threat: str
    Threats: str
    Title: str
    URL: str
    Vector: str
    Vulnerability: str


CVRF_XMLNS_MAP = dict(cvrf=CvrfNS._uri, prod=CvrfProdNS._uri, vuln=CvrfVulnNS._uri)


@dataclasses.dataclass(kw_only=True, frozen=True)
class ProductTree:
    ...


@dataclasses.dataclass(kw_only=True, frozen=True)
class CvrfDocument:
    product_tree: ProductTree


@dataclasses.dataclass(kw_only=True, frozen=True)
class Branch:
    type: str
    name: str

    @classmethod
    def vendor(cls, name: str) -> Branch:
        return cls(type="Vendor", name=name)

    @classmethod
    def family(cls, name: str) -> Branch:
        return cls(type="Product Family", name=name)


@dataclasses.dataclass(kw_only=True, frozen=True)
class FullProductName:
    full_product_name: str
    product_id: str | None
    branch_chain: list[Branch]


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


def download_year_listing(year_representative: datetime.datetime) -> pathlib.Path:
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
    if ignore_releases_before.year != now.year:
        downloaded_year_listings.append(download_year_listing(ignore_releases_before))
    downloaded_year_listings.append(download_year_listing(now))
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


def cvrf_find_products(
    cvrf_doc: ET.Element,
    branch_chain: list[Branch],
    full_product_name: str | None,
) -> typing.Generator[FullProductName, None, None]:
    product_tree = cvrf_doc.find(CvrfProdNS.ProductTree, namespaces=CVRF_XMLNS_MAP)
    epath = [product_tree]
    for link in branch_chain:
        for branch in epath[-1].iterfind(CvrfProdNS.Branch, namespaces=CVRF_XMLNS_MAP):
            n, t = branch.get("Name"), branch.get("Type")
            if t == link.type and n == link.name:
                epath.append(branch)
                break
            ic("could not find", link)
    for product_elem in epath[-1].iterfind(
        CvrfProdNS.FullProductName, namespaces=CVRF_XMLNS_MAP
    ):
        if full_product_name and product_elem.text == full_product_name:
            product = FullProductName(
                full_product_name=product_elem.text,
                product_id=product_elem.get("ProductID"),
                branch_chain=epath[1:],
            )
            yield product


def cvrf_get_product_id(
    cvrf_doc: ET.Element,
    branch_chain: list[Branch],
    full_product_name: str,
) -> str | None:
    for product in cvrf_find_products(cvrf_doc=cvrf_doc, branch_chain=branch_chain):
        if full_product_name == product.full_product_name:
            return product.product_id
    return None


if __name__ == "__main__":
    microsoft_branch = Branch.vendor("Microsoft")
    windows_branch = Branch.family("Windows")
    update_metadata_paths = download_updates_metadata()
    ic(update_metadata_paths)
    for ump in update_metadata_paths:
        tree = ET.parse(str(ump))
        root = tree.getroot()
        parent_map = {c: p for p in tree.iter() for c in p}
        watching_product_ids = [
            cvrf_get_product_id(
                cvrf_doc=root,
                branch_chain=[microsoft_branch, windows_branch],
                full_product_name="Windows 10 Version 21H2 for x64-based Systems",
            )
        ]
        ic(watching_product_ids)
        for p in cvrf_find_products(root, []):
            ic(p)

        # ET.dump(root.find(product_name_xpath))
        cutoff = 10
        for i, e in enumerate(root.iter()):
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
                case CvrfNS.Description:
                    ...
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
                case CvrfNS.Revision:
                    ...
                case CvrfNS.RevisionHistory:
                    ...
                case CvrfNS.Status:
                    ...
                case CvrfNS.Version:
                    ...
                case CvrfProdNS.Branch:
                    ...
                case CvrfProdNS.FullProductName:
                    ET.dump(e)
                    p = e
                    while p is not None:
                        ic(p, p.items())
                        p = parent_map.get(p)
                    break
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

from __future__ import annotations

import dataclasses
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from .helpers import xmlns

# TODO evaluate http://www.davekuhlman.org/generateDS.html to convert XMLSchema to Python

# TODO obtain XMLSchema
# Note: icasi.org redirects to first.org
# https://stix.mitre.org/language/version1.1.1/ has "All Files (offline)" (https://stix.mitre.org/language/version1.1.1/stix_v1.1.1_offline.zip)
# ... which includes CVRF xsd under .../external/cvrf_1.1/


@xmlns(uri="http://www.icasi.org/CVRF/schema/cvrf/1.1")
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


@xmlns(uri="http://www.icasi.org/CVRF/schema/prod/1.1")
class CvrfProdNS:
    Branch: str
    FullProductName: str
    ProductTree: str


CVRF_PROD_ATTR_TYPE = "Type"
CVRF_PROD_ATTR_NAME = "Name"
CVRF_PROD_ATTR_PRODUCT_ID = "ProductID"


@xmlns(uri="http://www.icasi.org/CVRF/schema/vuln/1.1")
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
class FullProductName:
    full_product_name: str
    product_id: str | None

    @classmethod
    def from_etree(cls, elem: ET.Element) -> CvrfDocument:
        _assert_cvrf_tag(elem, CvrfProdNS.FullProductName)
        return cls(
            full_product_name=elem.text, product_id=elem.get(CVRF_PROD_ATTR_PRODUCT_ID)
        )


@dataclasses.dataclass(kw_only=True, frozen=True)
class Branch:
    type: str
    name: str
    branches: list[Branch]
    full_product_names: list[FullProductName]

    @classmethod
    def from_etree(cls, elem: ET.Element) -> CvrfDocument:
        _assert_cvrf_tag(elem, CvrfProdNS.Branch)
        fpn_elems = elem.findall(CvrfProdNS.FullProductName)
        fpns = [FullProductName.from_etree(fpn) for fpn in fpn_elems]
        return cls(
            type=elem.get(CVRF_PROD_ATTR_TYPE),
            name=elem.get(CVRF_PROD_ATTR_NAME),
            branches=_find_and_make_branch_elements(elem),
            full_product_names=fpns,
        )


@dataclasses.dataclass(kw_only=True, frozen=True)
class ProductTree:
    branches: list[Branch]

    @classmethod
    def from_etree(cls, elem: ET.Element) -> CvrfDocument:
        _assert_cvrf_tag(elem, CvrfProdNS.ProductTree)
        return cls(branches=_find_and_make_branch_elements(elem))


@dataclasses.dataclass(kw_only=True, frozen=True)
class Number:
    value: str | None

    @classmethod
    def from_etree(cls, elem: ET.Element) -> Number:
        _assert_cvrf_tag(elem, CvrfNS.Number)
        return cls(value=elem.text)


@dataclasses.dataclass(kw_only=True, frozen=True)
class Date:
    dt: datetime | None

    @classmethod
    def from_etree(cls, elem: ET.Element) -> Date:
        _assert_cvrf_tag(elem, CvrfNS.Date)
        dt = datetime.fromisoformat(elem.text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return cls(dt=dt)


@dataclasses.dataclass(kw_only=True, frozen=True)
class Description:
    text: str | None

    @classmethod
    def from_etree(cls, elem: ET.Element) -> Description:
        _assert_cvrf_tag(elem, CvrfNS.Description)
        return cls(text=elem.text)


@dataclasses.dataclass(kw_only=True, frozen=True)
class Revision:
    number: Number | None
    date: Date | None
    description: Description | None

    @classmethod
    def from_etree(cls, elem: ET.Element) -> Revision:
        _assert_cvrf_tag(elem, CvrfNS.Revision)
        return cls(
            number=Number.from_etree(elem.find(CvrfNS.Number)),
            date=Date.from_etree(elem.find(CvrfNS.Date)),
            description=Description.from_etree(elem.find(CvrfNS.Description)),
        )


@dataclasses.dataclass(kw_only=True, frozen=True)
class CvrfDocument:
    # TODO verify that cvrfdoc has no more than one ProductTree
    product_tree: ProductTree

    @classmethod
    def from_etree(cls, elem: ET.Element) -> CvrfDocument:
        _assert_cvrf_tag(elem, CvrfNS.cvrfdoc)
        product_tree_elem = elem.find(CvrfProdNS.ProductTree)
        product_tree = ProductTree.from_etree(product_tree_elem)
        return cls(product_tree=product_tree)


def _find_and_make_branch_elements(elem: ET.Element):
    branch_elems = elem.findall(CvrfProdNS.Branch)
    branches = [Branch.from_etree(b) for b in branch_elems]
    return branches


def _assert_cvrf_tag(elem: ET.Element, expected_tag: str) -> None:
    if elem.tag != expected_tag:
        raise ValueError(f"Bad tag: got {elem.tag!r}, expected {expected_tag!r}")


def load_from_etree(tree: ET.ElementTree) -> CvrfDocument:
    cvrfdoc = CvrfDocument.from_etree(tree.getroot())
    return cvrfdoc

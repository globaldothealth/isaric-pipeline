import pandas as pd
from pandas.testing import assert_frame_equal
import os
from fhirflat.resources.organization import Organization

ORG_DICT_INPUT = {
    "resourceType": "Organization",
    "id": "f201",
    "identifier": [
        {
            "use": "official",
            "system": "http://www.zorgkaartnederland.nl/",
            "value": "Artis University Medical Center",
        }
    ],
    "active": True,
    "type": [
        {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "405608006",
                    "display": "Academic Medical Center",
                },
                {
                    "system": "urn:oid:2.16.840.1.113883.2.4.15.1060",
                    "code": "V6",
                    "display": "University Medical Hospital",
                },
                {
                    "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                    "code": "prov",
                    "display": "Healthcare Provider",
                },
            ]
        }
    ],
    "name": "Artis University Medical Center (AUMC)",
    "contact": [
        {
            "telecom": [{"system": "phone", "value": "+31715269111", "use": "work"}],
            "address": {
                "use": "work",
                "line": ["Walvisbaai 3"],
                "city": "Den Helder",
                "postalCode": "2333ZA",
                "country": "NLD",
            },
        },
        {
            "name": [
                {
                    "use": "official",
                    "text": "Professor Brand",
                    "family": "Brand",
                    "given": ["Ronald"],
                    "prefix": ["Prof.Dr."],
                }
            ],
            "telecom": [{"system": "phone", "value": "+31715269702", "use": "work"}],
            "address": {
                "line": ["Walvisbaai 3", "Gebouw 2"],
                "city": "Den helder",
                "postalCode": "2333ZA",
                "country": "NLD",
            },
        },
    ],
}

ORG_FLAT = {
    "resourceType": "Organization",
    "type.code": [
        [
            "http://snomed.info/sct|405608006",
            "urn:oid:2.16.840.1.113883.2.4.15.1060|V6",
            "http://terminology.hl7.org/CodeSystem/organization-type|prov",
        ]
    ],
    "type.text": [
        [
            "Academic Medical Center",
            "University Medical Hospital",
            "Healthcare Provider",
        ]
    ],
    "name": "Artis University Medical Center (AUMC)",
}

ORG_DICT_OUT = {
    "resourceType": "Organization",
    "active": True,
    "type": [
        {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "405608006",
                    "display": "Academic Medical Center",
                },
                {
                    "system": "urn:oid:2.16.840.1.113883.2.4.15.1060",
                    "code": "V6",
                    "display": "University Medical Hospital",
                },
                {
                    "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                    "code": "prov",
                    "display": "Healthcare Provider",
                },
            ]
        }
    ],
    "name": "Artis University Medical Center (AUMC)",
}


def test_organization_to_flat():
    bp = Organization(**ORG_DICT_INPUT)

    bp.to_flat("test_organization.parquet")

    assert_frame_equal(
        pd.read_parquet("test_organization.parquet"), pd.DataFrame(ORG_FLAT, index=[0])
    )
    os.remove("test_organization.parquet")


def test_organization_from_flat():
    visit = Organization(**ORG_DICT_OUT)

    flat_visit = Organization.from_flat("tests/data/organization_flat.parquet")

    assert visit == flat_visit

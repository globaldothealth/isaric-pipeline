import pandas as pd
from pandas.testing import assert_frame_equal
import os
from fhirflat.resources.immunization import Immunization
import datetime

IMMUNIZATION_DICT_INPUT = {
    "resourceType": "Immunization",
    "id": "reaction",
    "identifier": [
        {
            "system": "urn:ietf:rfc:3986",
            "value": "urn:oid:1.3.6.1.4.1.21367.2005.3.7.1234",
        }
    ],
    "status": "completed",
    "vaccineCode": {
        "coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": "175"}],
        "text": "Rabies - IM Diploid cell culture",
    },
    "manufacturer": {"reference": {"reference": "Organization/hl7"}},
    "lotNumber": "PPL909K",
    "expirationDate": "2023-01-21",
    "patient": {"reference": "Patient/example"},
    "encounter": {"reference": "Encounter/example"},
    "occurrenceDateTime": "2021-09-12",
    "primarySource": True,
    "location": {"reference": "Location/1"},
    "site": {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActSite",
                "code": "LA",
                "display": "left arm",
            }
        ]
    },
    "route": {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration",  # noqa:E501
                "code": "IM",
                "display": "Injection, intramuscular",
            }
        ]
    },
    "doseQuantity": {"value": 5, "system": "http://unitsofmeasure.org", "code": "mg"},
    "performer": [
        {
            "function": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0443",
                        "code": "OP",
                    }
                ]
            },
            "actor": {"reference": "Practitioner/example"},
        },
        {
            "function": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0443",
                        "code": "AP",
                    }
                ]
            },
            "actor": {"reference": "Practitioner/example"},
        },
    ],
    "note": [{"text": "Notes on adminstration of vaccine"}],
    "reason": [{"reference": {"reference": "Observation/example"}}],
    "isSubpotent": False,
    "reaction": [
        {
            "date": "2021-09-12",
            "manifestation": {"reference": {"reference": "Observation/example2"}},
            "reported": False,
        }
    ],
}

IMMUNIZATION_FLAT = {
    "resourceType": "Immunization",
    "occurrenceDateTime": datetime.date(2021, 9, 12),
    "reason.reference": "Observation/example",
    "isSubpotent": False,
    "reaction.date": datetime.date(2021, 9, 12),
    "reaction.reported": False,
    "reaction.manifestation.reference": "Observation/example2",
    "vaccineCode.code": "http://hl7.org/fhir/sid/cvx|175",
    "vaccineCode.text": "Rabies - IM Diploid cell culture",
    "manufacturer.reference": "Organization/hl7",
    "patient": "Patient/example",
    "encounter": "Encounter/example",
    "location": "Location/1",
    "site.code": "http://terminology.hl7.org/CodeSystem/v3-ActSite|LA",
    "site.text": "left arm",
    "route.code": "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration|IM",
    "route.text": "Injection, intramuscular",
    "doseQuantity.value": 5,
    "doseQuantity.code": "http://unitsofmeasure.org|mg",
}


def test_immunization_to_flat():
    vacc = Immunization(**IMMUNIZATION_DICT_INPUT)

    vacc.to_flat("test_immunization.parquet")

    assert_frame_equal(
        pd.read_parquet("test_immunization.parquet"),
        pd.DataFrame(IMMUNIZATION_FLAT, index=[0]),
        # Date types are off otherwise, pyarrow uses pytz and pandas uses dateutil
        check_dtype=False,
    )
    os.remove("test_immunization.parquet")


# def test_observation_from_flat():
#     visit = Encounter(**ENCOUNTER_DICT_OUT)

#     flat_visit = Encounter.from_flat("tests/data/encounter_flat.parquet")

#     assert visit == flat_visit

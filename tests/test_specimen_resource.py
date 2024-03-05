import pandas as pd
from pandas.testing import assert_frame_equal
import os
from fhirflat.resources.specimen import Specimen
import datetime

SPECIMEN_DICT_INPUT = {
    "resourceType": "Specimen",
    "id": "101",
    "status": "available",
    "type": {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "122555007",
                "display": "Venous blood specimen",
            }
        ]
    },
    "subject": {"reference": "Patient/example", "display": "Peter Patient"},
    "receivedTime": "2011-03-04T07:03:00Z",
    "request": [{"reference": "ServiceRequest/example"}],
    "collection": {
        "collector": {"reference": "Practitioner/example"},
        "collectedDateTime": "2011-05-30T06:15:00Z",
        "quantity": {"value": 6, "unit": "mL"},
        "method": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0488",
                    "code": "LNV",
                }
            ]
        },
        "bodySite": {
            "concept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "49852007",
                        "display": "Structure of median cubital vein (body structure)",
                    }
                ]
            }
        },
    },
    "container": [
        {
            "device": {
                "reference": "Device/device-example-specimen-container-green-gel-vacutainer"  # noqa:E501
            },
            "specimenQuantity": {"value": 3, "unit": "mL"},
        }
    ],
    "note": [{"text": "Specimen is grossly lipemic"}],
}

SPECIMEN_FLAT = {
    "resourceType": "Specimen",
    "receivedTime": datetime.datetime(2011, 3, 4, 7, 3),
    "request": "ServiceRequest/example",
    "container.device": "Device/device-example-specimen-container-green-gel-vacutainer",  # noqa:E501
    "container.specimenQuantity.value": 3,
    "container.specimenQuantity.unit": "mL",
    "type.code": "http://snomed.info/sct|122555007",
    "type.text": "Venous blood specimen",
    "subject": "Patient/example",
    "collection.collector": "Practitioner/example",
    "collection.collectedDateTime": datetime.datetime(2011, 5, 30, 6, 15),
    "collection.quantity.value": 6,
    "collection.quantity.unit": "mL",
    "collection.method.code": "http://terminology.hl7.org/CodeSystem/v2-0488|LNV",
    "collection.method.text": [[None]],
    "collection.bodySite.concept.code": "http://snomed.info/sct|49852007",
    "collection.bodySite.concept.text": "Structure of median cubital vein (body structure)",  # noqa:E501
}

SPECIMEN_DICT_OUT = {
    "resourceType": "Specimen",
    "type": {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "122555007",
                "display": "Venous blood specimen",
            }
        ]
    },
    "subject": {"reference": "Patient/example"},
    "receivedTime": "2011-03-04T07:03:00Z",
    "request": [{"reference": "ServiceRequest/example"}],
    "collection": {
        "collector": {"reference": "Practitioner/example"},
        "collectedDateTime": "2011-05-30T06:15:00Z",
        "quantity": {"value": 6, "unit": "mL"},
        "method": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0488",
                    "code": "LNV",
                }
            ]
        },
        "bodySite": {
            "concept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "49852007",
                        "display": "Structure of median cubital vein (body structure)",
                    }
                ]
            }
        },
    },
    "container": [
        {
            "device": {
                "reference": "Device/device-example-specimen-container-green-gel-vacutainer"  # noqa:E501
            },
            "specimenQuantity": {"value": 3, "unit": "mL"},
        }
    ],
}


def test_specimen_to_flat():
    vacc = Specimen(**SPECIMEN_DICT_INPUT)

    vacc.to_flat("test_specimen.parquet")

    assert_frame_equal(
        pd.read_parquet("test_specimen.parquet"),
        pd.DataFrame(SPECIMEN_FLAT, index=[0]),
        # Date types are off otherwise, pyarrow uses pytz and pandas uses dateutil
        check_dtype=False,
    )
    os.remove("test_specimen.parquet")


def test_specimen_from_flat():
    bld = Specimen(**SPECIMEN_DICT_OUT)

    flat_bld = Specimen.from_flat("tests/data/specimen_flat.parquet")

    assert bld == flat_bld

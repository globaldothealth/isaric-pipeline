import pandas as pd
from pandas.testing import assert_frame_equal
import os
from fhirflat.resources.procedure import Procedure
import datetime

PROCEDURE_DICT_INPUT = {
    "resourceType": "Procedure",
    "id": "f201",
    "instantiatesCanonical": ["http://example.org/fhir/PlanDefinition/KDN5"],
    "status": "completed",
    "code": {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "367336001",
                "display": "Chemotherapy",
            }
        ]
    },
    "subject": {"reference": "Patient/f201", "display": "Roel"},
    "encounter": {
        "reference": "Encounter/f202",
        "display": "Roel's encounter on January 28th, 2013",
    },
    "occurrencePeriod": {
        "start": "2013-01-28T13:31:00+01:00",
        "end": "2013-01-28T14:27:00+01:00",
    },
    "performer": [
        {
            "function": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "310512001",
                        "display": "Medical oncologist",
                    }
                ]
            },
            "actor": {"reference": "Practitioner/f201", "display": "Dokter Bronsig"},
        }
    ],
    "reason": [{"concept": {"text": "DiagnosticReport/f201"}}],
    "bodySite": [
        {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "272676008",
                    "display": "Sphenoid bone",
                }
            ]
        }
    ],
}

PROCEDURE_FLAT = {
    "resourceType": "Procedure",
    "bodySite.code": "http://snomed.info/sct|272676008",
    "bodySite.text": "Sphenoid bone",
    "code.code": "http://snomed.info/sct|367336001",
    "code.text": "Chemotherapy",
    "subject": "Patient/f201",
    "encounter": "Encounter/f202",
    "occurrencePeriod.start": datetime.datetime(
        2013, 1, 28, 13, 31, tzinfo=datetime.timezone(datetime.timedelta(minutes=60))
    ),
    "occurrencePeriod.end": datetime.datetime(
        2013, 1, 28, 14, 27, tzinfo=datetime.timezone(datetime.timedelta(minutes=60))
    ),
}

PROCEDURE_DICT_OUT = {
    "resourceType": "Procedure",
    "status": "completed",
    "code": {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "367336001",
                "display": "Chemotherapy",
            }
        ]
    },
    "subject": {"reference": "Patient/f201"},
    "encounter": {"reference": "Encounter/f202"},
    "occurrencePeriod": {
        "start": "2013-01-28T13:31:00+01:00",
        "end": "2013-01-28T14:27:00+01:00",
    },
    "bodySite": [
        {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "272676008",
                    "display": "Sphenoid bone",
                }
            ]
        }
    ],
}


def test_procedure_to_flat():
    bp = Procedure(**PROCEDURE_DICT_INPUT)

    bp.to_flat("test_procedure.parquet")

    assert_frame_equal(
        pd.read_parquet("test_procedure.parquet"),
        pd.DataFrame(PROCEDURE_FLAT, index=[0]),
        # Date types are off otherwise, pyarrow uses pytz and pandas uses dateutil
        check_dtype=False,
    )
    os.remove("test_procedure.parquet")


def test_observation_from_flat():
    chemo = Procedure(**PROCEDURE_DICT_OUT)

    flat_chemo = Procedure.from_flat("tests/data/procedure_flat.parquet")

    assert chemo == flat_chemo

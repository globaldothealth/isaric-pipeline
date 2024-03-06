import fhirflat.flat2fhir as f2f
import pytest
from fhir.resources.encounter import Encounter


@pytest.mark.parametrize(
    "data_groups, expected",
    [
        (
            (
                {"code.code": ["http://loinc.org|1234"], "code.text": ["Test"]},
                "code",
            ),
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "1234",
                        "display": "Test",
                    }
                ]
            },
        ),
        (
            (
                {
                    "code.code": [
                        "http://loinc.org|1234",
                        "http://snomed.info/sct|5678",
                    ],
                    "code.text": ["Test", "Snomed Test"],
                },
                "code",
            ),
            {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "1234",
                        "display": "Test",
                    },
                    {
                        "system": "http://snomed.info/sct",
                        "code": "5678",
                        "display": "Snomed Test",
                    },
                ]
            },
        ),
        (
            (
                {"code.code": [], "code.text": ["Test"]},
                "code",
            ),
            {
                "coding": [
                    {
                        "display": "Test",
                    }
                ]
            },
        ),
    ],
)
def test_create_codeable_concept(data_groups, expected):
    data, groups = data_groups
    result = f2f.create_codeable_concept(data, groups)

    assert result == expected


@pytest.mark.parametrize(
    "data_class, expected",
    [
        (
            (
                {
                    "admission.admitSource.code": ["http://snomed.info/sct|309902002"],
                    "admission.admitSource.text": ["Clinical Oncology Department"],
                    "admission.destination": {"reference": "Location/2"},
                    "admission.origin": {"reference": "Location/2"},
                },
                Encounter,
            ),
            {
                "admission": {
                    "admitSource": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "309902002",
                                "display": "Clinical Oncology Department",
                            }
                        ]
                    },
                    "destination": {"reference": "Location/2"},
                    "origin": {"reference": "Location/2"},
                }
            },
        ),
    ],
)
def test_expand_concepts(data_class, expected):
    data, data_class = data_class
    result = f2f.expand_concepts(data, data_class)

    assert result == expected

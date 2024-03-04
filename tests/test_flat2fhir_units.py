import fhirflat.flat2fhir as f2f
import pytest
from pytest_unordered import unordered


def test_group_keys():
    data = [
        "code.code",
        "code.text",
        "status",
        "class.code",
        "class.text",
        "priority.code",
        "priority.text",
        "type.code",
        "type.text",
        "participant.type.code",
        "participant.actor.reference",
    ]
    result = f2f.group_keys(data)

    assert result == unordered(
        [
            {"code": unordered(["code.code", "code.text"])},
            {"class": unordered(["class.code", "class.text"])},
            {"priority": unordered(["priority.code", "priority.text"])},
            {"type": unordered(["type.code", "type.text"])},
            {
                "participant": unordered(
                    ["participant.type.code", "participant.actor.reference"]
                )
            },
        ]
    )


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
    "data, expected",
    [
        (
            {"code.code": ["http://loinc.org|1234"], "code.text": ["Test"]},
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "1234",
                            "display": "Test",
                        }
                    ]
                }
            },
        ),
        (
            {
                "code.code": [
                    "http://loinc.org|1234",
                    "http://snomed.info/sct|5678",
                ],
                "code.text": ["Test", "Snomed Test"],
            },
            {
                "code": {
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
                }
            },
        ),
        (
            {
                "admission.admitSource.code": ["http://snomed.info/sct|309902002"],
                "admission.admitSource.text": ["Clinical Oncology Department"],
                "admission.destination": {"reference": "Location/2"},
                "admission.origin": {"reference": "Location/2"},
            },
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
def test_expand_concepts(data, expected):
    result = f2f.expand_concepts(data)

    assert result == expected

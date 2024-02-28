import fhirflat.flat2fhir as f2f
import pytest


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
    ],
)
def test_create_codeable_concept(data_groups, expected):
    data, groups = data_groups
    result = f2f.create_codeable_concept(data, groups)

    assert result == expected


@pytest.mark.parametrize(
    "data_groups, expected",
    [
        (
            (
                {"code.code": ["http://loinc.org|1234"], "code.text": ["Test"]},
                [{"code": ["code.code", "code.text"]}],
            ),
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
            (
                {
                    "code.code": [
                        "http://loinc.org|1234",
                        "http://snomed.info/sct|5678",
                    ],
                    "code.text": ["Test", "Snomed Test"],
                },
                [{"code": ["code.code", "code.text"]}],
            ),
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
    ],
)
def test_expand_concepts(data_groups, expected):
    data, groups = data_groups
    result = f2f.expand_concepts(data, groups)

    assert result == expected

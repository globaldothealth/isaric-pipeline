import pandas as pd
import fhirflat.fhir2flat as f2f
import pytest


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {"column1": [{"key1": "value1", "key2": "value2"}]},
            {"column1.key1": ["value1"], "column1.key2": ["value2"]},
        )
    ],
)
def test_flatten_column(data, expected):
    # Create a mock DataFrame
    df = pd.DataFrame(data)

    # Call the function
    result = f2f.flatten_column(df, "column1")

    # Check the result
    expected = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "code.coding": [
                    [{"system": "http://loinc.org", "code": "1234", "display": "Test"}]
                ]
            },
            {"code.code": [["http://loinc.org|1234"]], "code.text": [["Test"]]},
        ),
        (
            {
                "code.coding": [
                    [{"system": "http://loinc.org", "code": "1234", "display": "Test"}]
                ],
                "code.text": ["Test text"],
            },
            {"code.code": [["http://loinc.org|1234"]], "code.text": ["Test text"]},
        ),
        (
            {
                "code.coding": [
                    [
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
                ]
            },
            {
                "code.code": [["http://loinc.org|1234", "http://snomed.info/sct|5678"]],
                "code.text": [["Test", "Snomed Test"]],
            },
        ),
    ],
)
def test_expandCoding(data, expected):
    # Create a mock DataFrame
    df = pd.DataFrame(data)

    # Call the function
    result = f2f.expandCoding(df, "code.coding")

    # Check the result
    expected = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"subject.reference": ["Patient/example"]}, {"subject": ["Patient/example"]}),
        (
            {
                "subject.reference": ["Patient/example"],
                "subject.display": ["Donald Duck"],
            },
            {"subject": ["Patient/example"]},
        ),
    ],
)
def test_condenseReference(data, expected):
    # Create a mock DataFrame
    df = pd.DataFrame(data)

    # Call the function
    result = f2f.condenseReference(df, "subject.reference")

    # Check the result
    expected = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected)

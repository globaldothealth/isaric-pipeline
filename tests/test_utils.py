import pytest
from pytest_unordered import unordered
import fhirflat
from fhirflat.util import (
    group_keys,
    get_fhirtype,
    get_local_extension_type,
    get_local_resource,
)
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.medicationstatement import MedicationStatementAdherence

from fhirflat.resources.extensions import dateTimeExtension, Duration


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
    result = group_keys(data)

    assert result == {
        "code": unordered(["code.code", "code.text"]),
        "class": unordered(["class.code", "class.text"]),
        "priority": unordered(["priority.code", "priority.text"]),
        "type": unordered(["type.code", "type.text"]),
        "participant": unordered(
            ["participant.type.code", "participant.actor.reference"]
        ),
    }


@pytest.mark.parametrize(
    "input, expected",
    [
        ("Quantity", Quantity),
        ("CodeableConcept", CodeableConcept),
        ("MedicationStatementAdherence", MedicationStatementAdherence),
        ("dateTimeExtension", dateTimeExtension),
        ("duration", Duration),
    ],
)
def test_get_fhirtype(input, expected):
    result = get_fhirtype(input)
    assert result == expected


def test_get_fhirtype_import():
    # if 'Extension' is imported from fhir.resources.extension in this file the test
    # doesn't hit correct test point
    result = get_fhirtype("Extension")
    assert result.__module__ == "fhir.resources.extension"


def test_get_fhirtype_raises():
    with pytest.raises(AttributeError):
        get_fhirtype("NotARealType")


def test_get_local_extension_type_raises():
    with pytest.raises(
        AttributeError, match="Could not find NotARealType in fhirflat extensions"
    ):
        get_local_extension_type("NotARealType")


def test_get_local_resource():
    result = get_local_resource("Patient")
    assert result == fhirflat.Patient

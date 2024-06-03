import pandas as pd
from pandas.testing import assert_frame_equal
import os
from fhirflat.resources.location import Location

LOC_DICT_INPUT = {
    "resourceType": "Location",
    "id": "wash-dc-metro",
    "status": "active",
    "name": "Washington, DC metro area",
    "form": {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",  # noqa: E501
                "code": "area",
                "display": "Area",
            }
        ]
    },
    "endpoint": [{"reference": "Endpoint/1"}],
}

LOC_FLAT = {
    "resourceType": "Location",
    "name": "Washington, DC metro area",
    "form.code": "http://terminology.hl7.org/CodeSystem/location-physical-type|area",  # noqa: E501
    "form.text": "Area",
    "endpoint": "Endpoint/1",
}

LOC_DICT_OUT = {
    "resourceType": "Location",
    "name": "Washington, DC metro area",
    "form": {
        "coding": [
            {
                "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",  # noqa: E501
                "code": "area",
                "display": "Area",
            }
        ]
    },
    "endpoint": [{"reference": "Endpoint/1"}],
}


def test_location_to_flat():
    bp = Location(**LOC_DICT_INPUT)

    bp.to_flat("test_location.parquet")

    assert_frame_equal(
        pd.read_parquet("test_location.parquet"),
        pd.DataFrame(LOC_FLAT, index=[0]),
        check_like=True,
    )
    os.remove("test_location.parquet")


def test_location_from_flat():
    visit = Location(**LOC_DICT_OUT)

    flat_visit = Location.from_flat("tests/data/location_flat.parquet")

    assert visit == flat_visit

import pandas as pd
from pandas.testing import assert_frame_equal
import os
import datetime
from fhirflat.resources.patient import Patient

PATIENT_DICT_INPUT = {
    "id": "f001",
    "active": True,
    "name": [{"text": "Micky Mouse"}],
    "gender": "male",
    "deceasedBoolean": False,
    "address": [{"country": "Switzerland"}],
    "birthDate": "1996-05-30",
}

PATIENT_DICT_OUT = {
    "id": "f001",
    "gender": "male",
    "deceasedBoolean": False,
    "birthDate": "1996-05-30",
}


def test_patient_to_flat():
    patient = Patient(**PATIENT_DICT_INPUT)

    patient.to_flat("test_patient.parquet")

    assert_frame_equal(
        pd.read_parquet("test_patient.parquet"),
        pd.read_parquet("tests/data/patient_flat.parquet"),
    )
    os.remove("test_patient.parquet")


def test_single_patient_from_flat():
    patient = Patient(**PATIENT_DICT_OUT)

    flat_patient = Patient.from_flat("tests/data/patient_flat.parquet")

    assert patient == flat_patient


def test_multi_patient_from_flat():
    patients = Patient.from_flat("tests/data/multi_patient.parquet")

    assert len(patients) == 2

    assert patients[0] == Patient(**PATIENT_DICT_OUT)


def test_bulk_fhir_import_patient():
    patients = Patient.fhir_bulk_import("tests/data/patient.ndjson")

    assert len(patients) == 3


patient_ndjson_out = {
    # "index": [0, 0, 0],
    "resourceType": ["Patient", "Patient", "Patient"],
    "id": [
        "ewnMwMK-UNvVvM.bakFSlkw3",
        "exU8JSL0p8npSw5g1QYAyOw3",
        "ezER-U3fAMP-WvI-Fc8V9wQ3",
    ],
    "gender": ["female", "female", "male"],
    "birthDate": [
        datetime.date(2006, 10, 7),
        datetime.date(2019, 9, 21),
        datetime.date(1967, 1, 19),
    ],
    "deceasedBoolean": [False, False, False],
    "maritalStatus.text": ["Single", "Single", "Single"],
}


def test_bulk_fhir_to_flat_patient():
    Patient.fhir_file_to_flat(
        "tests/data/patient.ndjson", "multi_patient_output.parquet"
    )

    df = pd.read_parquet("multi_patient_output.parquet")
    df.reset_index(inplace=True, drop=True)
    assert_frame_equal(pd.DataFrame(patient_ndjson_out), df)
    os.remove("multi_patient_output.parquet")

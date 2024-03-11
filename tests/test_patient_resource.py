import pandas as pd
from pandas.testing import assert_frame_equal
import os
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

from fhirflat.ingest import load_data
from fhirflat.resources.encounter import Encounter
import pandas as pd
from pandas.testing import assert_frame_equal
import os


ENCOUNTER_SINGLE_ROW_FLAT = {
    "resourceType": "Encounter",
    "class.code": "https://snomed.info/sct|32485007",
    "class.text": "Hospital admission (procedure)",
    "reason.use.code": "https://snomed.info/sct|89100005",
    "reason.use.text": "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",  # noqa: E501
    "reason.value.concept.code": "https://snomed.info/sct|38362002",
    "reason.value.concept.text": "Dengue (disorder)",
    "diagnosis.condition.concept.code": "https://snomed.info/sct|722863008",
    "diagnosis.condition.concept.text": "Dengue with warning signs (disorder)",
    "diagnosis.use.code": "https://snomed.info/sct|89100005",
    "diagnosis.use.text": "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",  # noqa: E501
    "subject": "2",
    "actualPeriod.start": "2021-04-01 18:00:00",
    "actualPeriod.end": "2021-04-10",
    "admission.dischargeDisposition.code": "https://snomed.info/sct|371827001",
    "admission.dischargeDisposition.text": "Patient discharged alive (finding)",
}


def test_load_data_one_to_one_single_row():
    load_data(
        "tests/dummy_data/encounter_dummy_data_single.csv",
        "tests/dummy_data/encounter_dummy_mapping.csv",
        Encounter,
        "encounter_ingestion_single",
    )

    assert_frame_equal(
        pd.read_parquet("encounter_ingestion_single.parquet"),
        pd.DataFrame([ENCOUNTER_SINGLE_ROW_FLAT], index=[0]),
        check_dtype=False,
    )
    os.remove("encounter_ingestion_single.parquet")


ENCOUNTER_SINGLE_ROW_MULTI = {
    "resourceType": ["Encounter", "Encounter", "Encounter", "Encounter"],
    "class.code": [
        "https://snomed.info/sct|32485007",
        "https://snomed.info/sct|32485007",
        "https://snomed.info/sct|32485007",
        "https://snomed.info/sct|32485007",
    ],
    "class.text": [
        "Hospital admission (procedure)",
        "Hospital admission (procedure)",
        "Hospital admission (procedure)",
        "Hospital admission (procedure)",
    ],
    "reason.use.code": [
        None,
        "https://snomed.info/sct|89100005",
        "https://snomed.info/sct|89100005",
        None,
    ],
    "reason.use.text": [
        None,
        "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",
        "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",
        None,
    ],
    "reason.value.concept.code": [
        None,
        "https://snomed.info/sct|38362002",
        "https://snomed.info/sct|38362002",
        None,
    ],
    "reason.value.concept.text": [None, "Dengue (disorder)", "Dengue (disorder)", None],
    "diagnosis.condition.concept.code": [
        None,
        "https://snomed.info/sct|722863008",
        "https://snomed.info/sct|722862003",
        None,
    ],
    "diagnosis.condition.concept.text": [
        None,
        "Dengue with warning signs (disorder)",
        "Dengue without warning signs (disorder)",
        None,
    ],
    "diagnosis.use.code": [
        None,
        "https://snomed.info/sct|89100005",
        "https://snomed.info/sct|89100005",
        "https://snomed.info/sct|89100005",
    ],
    "diagnosis.use.text": [
        None,
        "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",
        "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",
        "Final diagnosis (discharge) (contextual qualifier) (qualifier value)",
    ],
    "subject": ["1", "2", "3", "4"],
    "actualPeriod.start": [
        "2020-05-01",
        "2021-04-01 18:00:00",
        "2021-05-10 17:30:00",
        "2022-06-15 21:00:00",
    ],
    "actualPeriod.end": [
        "2020-05-01",
        "2021-04-10",
        "2021-05-15",
        "2022-06-20",
    ],
    "admission.dischargeDisposition.code": [
        "https://snomed.info/sct|371827001",
        "https://snomed.info/sct|371827001",
        "https://snomed.info/sct|419099009",
        "https://snomed.info/sct|32485007",
    ],
    "admission.dischargeDisposition.text": [
        "Patient discharged alive (finding)",
        "Patient discharged alive (finding)",
        "Dead (finding)",
        "Hospital admission (procedure)",
    ],
}


def test_load_data_one_to_one_multi_row():
    load_data(
        "tests/dummy_data/encounter_dummy_data_multi.csv",
        "tests/dummy_data/encounter_dummy_mapping.csv",
        Encounter,
        "encounter_ingestion_multi",
    )

    assert_frame_equal(
        pd.read_parquet("encounter_ingestion_multi.parquet"),
        pd.DataFrame(ENCOUNTER_SINGLE_ROW_MULTI),
        check_dtype=False,
        check_like=True,
    )
    os.remove("encounter_ingestion_multi.parquet")

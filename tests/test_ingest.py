from fhirflat.ingest import load_data
from fhirflat.resources.encounter import Encounter
import pandas as pd
from pandas.testing import assert_frame_equal
import datetime
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
    "actualPeriod.start": datetime.datetime(2021, 4, 1, 18, 0),
    "actualPeriod.end": datetime.date(2021, 4, 10),
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

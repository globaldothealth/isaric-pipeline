from fhirflat.ingest import load_data
from fhirflat.resources.encounter import Encounter
import pandas as pd


def test_load_data_one_to_one_single_row():
    load_data(
        "tests/dummy_data/encounter_dummy_data_single.csv",
        "tests/dummy_data/encounter_dummy_mapping.csv",
        Encounter,
        "encounter_ingestion_single",
    )

    pd.read_parquet("encounter_ingestion_single.parquet")

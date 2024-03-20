"""
Synthgen module to generate synthetic data for the ISARIC 3.0 pipeline

Usage:
  synthgen -c config.ini 100000000

Output:
 - output bundles for each patient in output/fhir
 - FHIRFlat files in output/fhirflat, one parquet file for each resource

TODO: Define configuration file format
"""

import json
from datetime import datetime
from dataclasses import dataclass
from collections import namedtuple
from pathlib import Path

Code = namedtuple("Code", "code text")

# TODO: Encounter distribution: 1 root encounter 90%, 2 root encounters 10%. A
# root encounter is one without any parent -- unlike ICU encounters which will
# be linked to a parent hospitalization encounter.

# TODO: Treatment or intervention duration is in days and is Poisson
# distributed. Treatment data is nested according to core disease type e.g.
# COVID-19 is going to have oxygen therapy but not dengue.

# TODO: Comorbidity distributions could be taken from aggregate data, with age
# buckets.

@dataclass
class BucketValue:
    bucket: range
    value: float


@dataclass
class AgeDistribution:
    items: list[BucketValue]
    maximum: 120
    minimum: 0

    def generate(self) -> float:
        return 1


class Rate:
    data: list[float] = []

    def __init__(self, items: list[BucketValue], maximum_age: int = 120):
        # do something and create data
        ...

    def __getitem__(self, age: int) -> float:
        if age > len(self.data) - 1:
            raise ValueError("age beyond maximum of")
        return self.data[age]


class ComorbidityDistribution:

    def __init__(self, data: str):
        with open(data) as fp:
            self.data = json.load(fp)


class TreatmentLibrary:

    def __init__(self, data: str):
        with open(data) as fp:
            self.data = json.load(fp)


class SynthGen:

    def __init__(
        self,
        seed: int,
        disease: Code,
        observation_period: tuple[datetime, datetime],
        age_distribution: AgeDistribution,
        mortality_rate: Rate,
        hospitalization_rate: Rate,
        icu_rate: Rate,
        comorbidity_distribution_data: str,
        treatment_options_data: str,
    ):
        self.seed = seed  # random seed
        self.disease = disease
        self.startPeriod = observation_period[0]
        self.endPeriod = observation_period[1]
        assert (
            self.startPeriod < self.endPeriod
        ), "Observation period start should be before end"
        self.age_distribution = age_distribution
        self.mortality_rate = mortality_rate
        self.hospitalization_rate = hospitalization_rate
        self.icu_rate = icu_rate
        self.comorbidity_distribution = ComorbidityDistribution(
            comorbidity_distribution_data
        )
        self.treatments = TreatmentLibrary(treatment_options_data)

    def generate_single_patient(self) -> dict[str, str]:
        "Generates FHIR data for a single patient"
        ...

    def generate_population(n: int, output_folder: Path):
        "Writes output data in FHIR Bundle and FHIRFlat"
        ...

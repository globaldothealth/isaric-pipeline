from __future__ import annotations

from typing import ClassVar, TypeAlias, Union

import orjson
from fhir.resources import fhirtypes
from fhir.resources.encounter import Encounter as _Encounter
from fhir.resources.encounter import (
    EncounterAdmission,
    EncounterDiagnosis,
    EncounterLocation,
    EncounterParticipant,
    EncounterReason,
)
from pydantic.v1 import Field, ValidationError, validator

from fhirflat.flat2fhir import expand_concepts

from .base import FHIRFlatBase
from .extension_types import relativePeriodType, timingPhaseType
from .extensions import relativePeriod, timingPhase

JsonString: TypeAlias = str


class Encounter(_Encounter, FHIRFlatBase):
    extension: list[
        Union[relativePeriodType, timingPhaseType, fhirtypes.ExtensionType]
    ] = Field(
        None,
        alias="extension",
        title="List of `Extension` items (represented as `dict` in JSON)",
        description=(
            """
            Contains the Global.health 'eventTiming' and 'relativePeriod' extensions,
            and allows extensions from other implementations to be included.
            """
        ),
        # if property is element of this resource.
        element_property=True,
        # this trys to match the type of the object to each of the union types
        union_mode="smart",
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions | {
        "identifier",
        "participant",  # participants other than the patient
        "appointment",  # appointment that scheduled the encounter
        "account",  # relates to billing
        "dietPreference",
        "specialArrangement",  # if translator, streatcher, wheelchair etc. needed
        "specialCourtesy",  # contains ID information, VIP, board member, etc.
    }

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = [*FHIRFlatBase.flat_defaults, "status"]

    backbone_elements: ClassVar[dict] = {
        "participant": EncounterParticipant,
        "reason": EncounterReason,
        "diagnosis": EncounterDiagnosis,
        "admission": EncounterAdmission,
        "location": EncounterLocation,
    }

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        rel_phase_count = sum(isinstance(item, relativePeriod) for item in extensions)
        tim_phase_count = sum(isinstance(item, timingPhase) for item in extensions)

        if rel_phase_count > 1 or tim_phase_count > 1:
            raise ValueError("relativePeriod and timingPhase can only appear once.")

        return extensions

    @classmethod
    def cleanup(cls, data_dict: JsonString | dict, json_data=True) -> Encounter:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        if json_data and isinstance(data_dict, str):
            data: dict = orjson.loads(data_dict)
        elif isinstance(data_dict, dict):
            data: dict = data_dict

        for field in {
            "subject",
            "episodeOfCare",
            "basedOn",
            "careTeam",
            "partOf",
            "serviceProvider",
            "admission.destination",
            "admission.origin",
        }.intersection(data.keys()):
            data[field] = {"reference": data[field]}

        # add default status back in
        data["status"] = "completed"

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if not isinstance(data[field], list):
                data[field] = [data[field]]

        try:
            return cls(**data)
        except ValidationError as e:
            return e

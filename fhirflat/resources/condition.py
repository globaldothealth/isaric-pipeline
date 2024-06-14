from __future__ import annotations

from typing import ClassVar, TypeAlias, Union

import orjson
from fhir.resources import fhirtypes
from fhir.resources.condition import Condition as _Condition
from pydantic.v1 import Field, ValidationError, validator

from fhirflat.flat2fhir import expand_concepts

from .base import FHIRFlatBase
from .extension_types import presenceAbsenceType, prespecifiedQueryType, timingPhaseType
from .extensions import presenceAbsence, prespecifiedQuery, timingPhase

JsonString: TypeAlias = str

# TODO: Update references to disallow "display" (could contain names)


class Condition(_Condition, FHIRFlatBase):
    extension: list[
        Union[
            presenceAbsenceType,
            prespecifiedQueryType,
            timingPhaseType,
            fhirtypes.ExtensionType,
        ]
    ] = Field(
        None,
        alias="extension",
        title="Additional content defined by implementations",
        description=(
            """
            Contains the G.H 'age' and 'birthSex' extensions,
            and allows extensions from other implementations to be included."""
        ),
        # if property is element of this resource.
        element_property=True,
        union_mode="smart",
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions | {
        "id",
        "identifier",
        "verificationStatus",
        "evidence",
        "note",
        "participant",
    }

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = [*FHIRFlatBase.flat_defaults, "clinicalStatus"]

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        present_count = sum(isinstance(item, presenceAbsence) for item in extensions)
        query_count = sum(isinstance(item, prespecifiedQuery) for item in extensions)
        timing_count = sum(isinstance(item, timingPhase) for item in extensions)

        if present_count > 1 or query_count > 1 or timing_count > 1:
            raise ValueError(
                "presenceAbsence, prespecifiedQuery and timingPhase can only appear"
                " once."
            )

        return extensions

    @classmethod
    def cleanup(cls, data_dict: JsonString | dict, json_data=True) -> Condition:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        if json_data and isinstance(data_dict, str):
            data: dict = orjson.loads(data_dict)
        elif isinstance(data_dict, dict):
            data: dict = data_dict

        for field in ({"patient", "encounter"}).intersection(data.keys()):
            data[field] = {"reference": data[field]}

        # add default clinicalStatus back in
        data["clinicalStatus"] = {
            "coding": [
                {
                    "system": (
                        "http://terminology.hl7.org/CodeSystem/condition-clinical"
                    ),
                    "code": "unknown",
                }
            ]
        }

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if not isinstance(data[field], list):
                data[field] = [data[field]]

        try:
            return cls(**data)
        except ValidationError as e:
            return e

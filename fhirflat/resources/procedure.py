from __future__ import annotations

from typing import ClassVar, TypeAlias, Union

import orjson
from fhir.resources import fhirtypes
from fhir.resources.procedure import Procedure as _Procedure
from pydantic.v1 import Field, ValidationError, validator

from fhirflat.flat2fhir import expand_concepts

from .base import FHIRFlatBase
from .extension_types import (
    dateTimeExtensionType,
    durationType,
    relativePeriodType,
    timingPhaseType,
)
from .extensions import Duration, relativePeriod, timingPhase

JsonString: TypeAlias = str


class Procedure(_Procedure, FHIRFlatBase):
    extension: list[
        Union[
            durationType, timingPhaseType, relativePeriodType, fhirtypes.ExtensionType
        ]
    ] = Field(
        None,
        alias="extension",
        title="Additional content defined by implementations",
        description=(
            """
            Contains the G.H 'timingPhase', 'relativePeriod' and 'duration' extensions,
            and allows extensions from other implementations to be included."""
        ),
        # if property is element of this resource.
        element_property=True,
        union_mode="smart",
    )

    occurrenceDateTime__ext: dateTimeExtensionType = Field(
        None,
        alias="_occurrenceDateTime",
        title="Extension field for ``occurrenceDateTime``.",
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions | {
        "id",
        "identifier",
        "instantiatesCanonical",
        "instantiatesUri",
        "basedOn",
        "statusReason",
        "focus",
        "reportedBoolean",
        "reportedReference",
        "performer",
        "reason",
        "note",
        "supportingInfo",
    }

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = [*FHIRFlatBase.flat_defaults, "status"]

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        duration_count = sum(isinstance(item, Duration) for item in extensions)
        tim_phase_count = sum(isinstance(item, timingPhase) for item in extensions)
        rel_phase_count = sum(isinstance(item, relativePeriod) for item in extensions)

        if duration_count > 1 or tim_phase_count > 1 or rel_phase_count > 1:
            raise ValueError(
                "duration, timingPhase and relativePeriod can only appear once."
            )

        return extensions

    @classmethod
    def cleanup(
        cls, data_dict: JsonString | dict, json_data=True
    ) -> Procedure | ValidationError:
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
            "partOf",
            "encounter",
            "subject",
            "recorder",
            "performer",
            "location",
            "report",
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

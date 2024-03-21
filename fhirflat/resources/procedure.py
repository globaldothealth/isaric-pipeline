from __future__ import annotations
from fhir.resources.procedure import Procedure as _Procedure
from .base import FHIRFlatBase
from .extensions import dateTimeExtension, procedureExtension, relativePhaseExtension
from pydantic.v1 import Field
import orjson

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class Procedure(_Procedure, FHIRFlatBase):

    extension: procedureExtension = Field(
        None,
        alias="extension",
        title="Additional content defined by implementations",
        description=(
            """
            Contains the G.H 'timingPhase' and 'duration' extensions, and allows
             extensions from other implementations to be included."""
        ),
        # if property is element of this resource.
        element_property=True,
    )

    occurrenceDateTime__ext: dateTimeExtension = Field(
        None,
        alias="_occurrenceDateTime",
        title="Extension field for ``occurrenceDateTime``.",
    )

    occurrencePeriod__ext: relativePhaseExtension = Field(
        None,
        alias="_occurrencePeriod",
        title="Extension field for ``occurrencePeriod``.",
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
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
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = FHIRFlatBase.flat_defaults + ["status"]

    @classmethod
    def cleanup(cls, data: JsonString) -> Procedure:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        data = orjson.loads(data)

        for field in [
            "partOf",
            "encounter",
            "subject",
            "recorder",
            "performer",
            "location",
            "report",
        ]:
            if field in data.keys():
                data[field] = {"reference": data[field]}

        # add default status back in
        data["status"] = "completed"

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if type(data[field]) is not list:
                data[field] = [data[field]]

        return cls(**data)

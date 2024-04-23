from __future__ import annotations
from fhir.resources.immunization import Immunization as _Immunization
from .base import FHIRFlatBase
from .extensions import timingPhase
from .extension_types import timingPhaseType, dateTimeExtensionType
from pydantic.v1 import Field, validator
import orjson

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar, Union
from fhir.resources import fhirtypes

JsonString: TypeAlias = str


class Immunization(_Immunization, FHIRFlatBase):

    extension: list[Union[timingPhaseType, fhirtypes.ExtensionType]] = Field(
        None,
        alias="extension",
        title="List of `Extension` items (represented as `dict` in JSON)",
        description=(
            """
            Contains the G.H 'eventPhase' extension, and allows extensions from other
             implementations to be included."""
        ),
        # if property is element of this resource.
        element_property=True,
        # this trys to match the type of the object to each of the union types
        union_mode="smart",
    )

    occurrenceDateTime__ext: dateTimeExtensionType = Field(
        None,
        alias="_occurrenceDateTime",
        title="Extension field for ``occurrenceDateTime``.",
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
        "id",
        "identifier",
        "basedOn",
        "statusReason",
        "administeredProduct",
        "lotNumber",
        "expirationDate",
        "supportingInformation",
        "primarySource",
        "informationSource",
        "performer",
        "note",
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = FHIRFlatBase.flat_defaults + ["status"]

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        phase_count = sum(isinstance(item, timingPhase) for item in extensions)

        if phase_count > 1:
            raise ValueError("timingPhase can only appear once.")

        return extensions

    @classmethod
    def cleanup(cls, data: JsonString) -> Immunization:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        data = orjson.loads(data)

        for field in ["patient", "encounter", "location"] + [
            x for x in data.keys() if x.endswith(".reference")
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

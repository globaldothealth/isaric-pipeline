from __future__ import annotations
from fhir.resources.observation import Observation as _Observation
from fhir.resources.observation import ObservationComponent as _ObservationComponent

from .base import FHIRFlatBase
from .extension_types import dateTimeExtensionType, timingPhaseExtensionType
from pydantic.v1 import Field
import orjson

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class ObservationComponent(_ObservationComponent):
    """
    Adds the dateTime extension into the Observation.component class
    """

    valueDateTime__ext: dateTimeExtensionType = Field(
        None,
        alias="_effectiveDateTime",
        title="Extension field for ``effectiveDateTime``.",
    )


class Observation(_Observation, FHIRFlatBase):

    extension: timingPhaseExtensionType = Field(
        None,
        alias="extension",
        title="Additional content defined by implementations",
        description=(
            """
            Contains the G.H 'eventPhase' extension, and allows extensions from other
             implementations to be included."""
        ),
        # if property is element of this resource.
        element_property=True,
    )

    effectiveDateTime__ext: dateTimeExtensionType = Field(
        None,
        alias="_effectiveDateTime",
        title="Extension field for ``effectiveDateTime``.",
    )

    # Update component to include the dateTime extension
    component: list[ObservationComponent] = Field(
        None,
        alias="component",
        title="Component results",
        description=(
            "Some observations have multiple component observations.  These "
            "component observations are expressed as separate code value pairs that"
            " share the same attributes.  Examples include systolic and diastolic "
            "component observations for blood pressure measurement and multiple "
            "component observations for genetics observations."
        ),
        # if property is element of this resource.
        element_property=True,
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
        "id",
        "identifier",
        "instantiatesCanonical",
        "instantiatesReference",
        "basedOn",
        "focus",
        "referenceRange",
        "issued",
        "note",
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = FHIRFlatBase.flat_defaults + ["status"]

    @classmethod
    def cleanup(cls, data: JsonString) -> Observation:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        data = orjson.loads(data)

        for field in [
            "encounter",
            "subject",
            "performer",
            "bodyStructure",
            "specimen",
            "device",
        ]:
            if field in data.keys():
                data[field] = {"reference": data[field]}

        # add default status back in
        data["status"] = "final"

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if type(data[field]) is not list:
                data[field] = [data[field]]

        return cls(**data)

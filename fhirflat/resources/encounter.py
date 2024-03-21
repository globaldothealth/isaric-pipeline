from __future__ import annotations
from fhir.resources.encounter import Encounter as _Encounter
from .base import FHIRFlatBase
import orjson

from ..flat2fhir import expand_concepts
from .extensions import relativeTimingPhaseExtension
from pydantic.v1 import Field
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class Encounter(_Encounter, FHIRFlatBase):

    extension: relativeTimingPhaseExtension = Field(
        None,
        alias="extension",
        title="Additional content defined by implementations",
        description=(
            """
            Contains the G.H 'eventTiming' and 'relativePhase' extensions, and allows
             extensions from other implementations to be included.
            """
        ),
        # if property is element of this resource.
        element_property=True,
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
        "id",
        "identifier",
        "participant",  # participants other than the patient
        "appointment",  # appointment that scheduled the encounter
        "account",  # relates to billing
        "dietPreference",
        "specialArrangement",  # if translator, streatcher, wheelchair etc. needed
        "specialCourtesy",  # contains ID information, VIP, board member, etc.
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = FHIRFlatBase.flat_defaults + ["status"]

    @classmethod
    def cleanup(cls, data: JsonString) -> Encounter:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        data = orjson.loads(data)

        for field in [
            "subject",
            "episodeOfCare",
            "basedOn",
            "careTeam",
            "partOf",
            "serviceProvider",
            "admission.destination",
            "admission.origin",
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

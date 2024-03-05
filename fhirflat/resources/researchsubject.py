from __future__ import annotations
from fhir.resources.researchsubject import ResearchSubject as _ResearchSubject
from .base import FHIRFlatBase
import orjson

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class ResearchSubject(_ResearchSubject, FHIRFlatBase):

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
        "id",
        "identifier",
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = FHIRFlatBase.flat_defaults + ["status"]

    @classmethod
    def cleanup(cls, data: JsonString) -> ResearchSubject:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        data = orjson.loads(data)

        for field in ["study", "subject", "consent"] + [
            x for x in data.keys() if x.endswith(".reference")
        ]:
            if field in data.keys():
                data[field] = {"reference": data[field]}

        # add default status back in
        data["status"] = "active"

        data = expand_concepts(data)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            data[field] = [data[field]]

        return cls(**data)

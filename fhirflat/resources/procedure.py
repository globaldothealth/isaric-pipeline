from fhir.resources.procedure import Procedure
from .base import FHIRFlatBase
import orjson
from itertools import groupby

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class Procedure(Procedure, FHIRFlatBase):
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

        # find and group keys belonging to the same concept
        grouped_keys = [k for k in data.keys() if "." in k]
        grouped_keys.sort()
        groups = [
            {k: [gs for gs in g]}
            for k, g in groupby(grouped_keys, lambda x: x.split(".")[0])
        ]
        data = expand_concepts(data, groups)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            data[field] = [data[field]]

        return cls(**data)

from __future__ import annotations
from fhir.resources.specimen import Specimen as _Specimen
from .base import FHIRFlatBase
import orjson

from fhirflat.flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class Specimen(_Specimen, FHIRFlatBase):

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions | {
        "id",
        "identifier",
        "accessionIdentifier",
        "status",
        "note",
    }

    @classmethod
    def cleanup(cls, data_dict: JsonString | dict, json_data=True) -> Specimen:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        if json_data and isinstance(data_dict, str):
            data: dict = orjson.loads(data_dict)
        elif isinstance(data_dict, dict):
            data: dict = data_dict

        for field in (
            {
                "subject",
                "parent",
                "request",
                "collection.collector",
                "collection.procedure",
                "container.device",
                "container.location",
            }
            | {x for x in data.keys() if x.endswith(".reference")}
        ).intersection(data.keys()):
            data[field] = {"reference": data[field]}

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if type(data[field]) is not list:
                data[field] = [data[field]]

        return cls(**data)

from __future__ import annotations

from typing import ClassVar, TypeAlias

import orjson
from fhir.resources.organization import Organization as _Organization

from fhirflat.flat2fhir import expand_concepts

from .base import FHIRFlatBase

JsonString: TypeAlias = str


class Organization(_Organization, FHIRFlatBase):

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions | {
        "id",
        "identifier",
        "active",
        "contact",  # phone numbers, addresses
    }

    @classmethod
    def cleanup(cls, data_dict: JsonString | dict, json_data=True) -> Organization:
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
            "endpoint",
            "qualification.issuer",
        }.intersection(data.keys()):
            data[field] = {"reference": data[field]}

        # add default status back in
        data["active"] = True

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if not isinstance(data[field], list):
                data[field] = [data[field]]

        return cls(**data)

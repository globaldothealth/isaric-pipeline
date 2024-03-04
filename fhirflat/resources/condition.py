from fhir.resources.condition import Condition
from .base import FHIRFlatBase
import orjson

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str

# TODO: Update references to disallow "display" (could contain names)


class Condition(Condition, FHIRFlatBase):
    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
        "id",
        "identifier",
        "verificationStatus",
        "evidence",
        "note",
        "participant",
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = FHIRFlatBase.flat_defaults + ["clinicalStatus"]

    @classmethod
    def flat_descriptions(cls) -> dict[str, str]:
        """
        Descriptions of the fields in the FHIRflat representation
        For use in LLM discussions & parser generation
        """
        descrip = {
            field: cls.__fields__[field].field_info.description
            for field in cls.flat_fields()
        }

        descrip["code"] = "Lists the condition, problem or diagnosis."
        descrip["subject"] = "The patient's identification number."

        return descrip

    @classmethod
    def cleanup(cls, data: JsonString) -> Condition:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        data = orjson.loads(data)

        data["encounter"] = {"reference": data["encounter"]}
        data["subject"] = {"reference": data["subject"]}

        # add default clinicalStatus back in
        data["clinicalStatus"] = {
            "coding": [
                {
                    "system": (
                        "http://terminology.hl7.org/CodeSystem/" "condition-clinical"
                    ),
                    "code": "unknown",
                }
            ]
        }

        data = expand_concepts(data)

        # create lists for properties which are lists of FHIR types
        # FIXUP: This is not elegant, or fast
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            data[field] = [data[field]]

        return cls(**data)

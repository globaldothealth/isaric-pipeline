from fhir.resources.patient import Patient
from .base import FHIRFlatBase
from .extension_types import (
    ageType,
    birthSexType,
)
from .extensions import Age, birthSex
import orjson

from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar, Union
from fhir.resources import fhirtypes
from pydantic.v1 import Field, validator

JsonString: TypeAlias = str


class Patient(Patient, FHIRFlatBase):
    extension: list[Union[ageType, birthSexType, fhirtypes.ExtensionType]] = Field(
        None,
        alias="extension",
        title="Additional content defined by implementations",
        description=(
            """
            Contains the G.H 'age' and 'birthSex' extensions,
            and allows extensions from other implementations to be included."""
        ),
        # if property is element of this resource.
        element_property=True,
        union_mode="smart",
    )

    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = FHIRFlatBase.flat_exclusions + (
        "identifier",
        "active",
        "name",
        "telecom",
        "address",
        "photo",
        "contact",
        "communication",
        "link",
    )

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        age_count = sum(isinstance(item, Age) for item in extensions)
        birthsex_count = sum(isinstance(item, birthSex) for item in extensions)

        if age_count > 1 or birthsex_count > 1:
            raise ValueError("Age and birthSex can only appear once.")

        return extensions

    @classmethod
    def flat_descriptions(cls) -> dict[str, str]:
        "Descriptions of the fields in the FHIRflat representation"
        descrip = {
            field: cls.__fields__[field].field_info.description
            for field in cls.flat_fields()
        }

        descrip["id"] = "The identifier or identification number for the patient."
        descrip["gender"] = "The sex, sex at birth or gender of the patient."
        descrip["deceasedBoolean"] = "Indicates if the patient has died."
        descrip["deceasedDateTime"] = "Date of death if the patient has died."

        return descrip

    @classmethod
    def cleanup(cls, data: JsonString) -> Patient:
        # Load the data and apply resource-specific changes
        data = orjson.loads(data)

        # # Strip time from the birthDate
        if "birthDate" in data:
            data["birthDate"] = data["birthDate"].split("T", 1)[0]

        data = expand_concepts(data, cls)

        # create lists for properties which are lists of FHIR types
        for field in [x for x in data.keys() if x in cls.attr_lists()]:
            if type(data[field]) is not list:
                data[field] = [data[field]]

        return cls(**data)

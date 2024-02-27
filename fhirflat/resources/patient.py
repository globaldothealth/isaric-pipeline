from fhir.resources.patient import Patient
from .base import FHIRFlatBase
import orjson
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class Patient(Patient, FHIRFlatBase):
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

        # Strip time from the birthDate
        data["birthDate"] = data["birthDate"].split("T", 1)[0]

        return cls(**data)

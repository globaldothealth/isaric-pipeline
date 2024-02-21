from fhir.resources.patient import Patient
import orjson
import pandas as pd
from ..fhir2flat import fhir2flat
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class Patient(Patient):
    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = (
        "meta",
        "implicitRules",
        "language",
        "text",
        "contained",
        "modifierExtension",
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
    def flat_fields(cls) -> list[str]:
        "All fields that are present in the FHIRflat representation"
        return [x for x in cls.elements_sequence() if x not in cls.flat_exclusions]

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
    def from_flat(cls, file: str) -> Patient | list[Patient]:
        """
        Takes a FHIRflat pandas dataframe and populates the resource with the data.

        file: parquet file
            FHIRflat file containing patient data
        """

        def cleanup(cls, data: JsonString) -> Patient:
            # Load the data and apply resource-specific changes
            data = orjson.loads(data)

            # Strip time from the birthDate
            data["birthDate"] = data["birthDate"].split("T", 1)[0]

            return cls(**data)

        df = pd.read_parquet(file)

        df["json_data"] = df.apply(
            lambda row: row.to_json(date_format="iso", date_unit="s"), axis=1
        )
        df["fhir"] = df["json_data"].apply(lambda x: cleanup(cls, x))

        if len(df) == 1:
            return df["fhir"].iloc[0]
        else:
            return list(df["fhir"])

    def to_flat(self, filename: str) -> None:
        """
        Generates a FHIRflat parquet file from the resource.

        filename: str
            Name of the parquet file to be generated.

        Returns
        -------
        parquet file
            FHIRflat file containing patient data
        """
        # clear data from attributes not used in FHIRflat
        for field in [x for x in self.elements_sequence() if x in self.flat_exclusions]:
            setattr(self, field, None)

        flat_df = fhir2flat(self)

        return flat_df.to_parquet(filename)

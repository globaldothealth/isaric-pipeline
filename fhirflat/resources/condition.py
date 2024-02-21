from fhir.resources.condition import Condition
import orjson
from itertools import groupby

import pandas as pd

from ..fhir2flat import fhir2flat
from ..flat2fhir import expand_concepts
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str

# TODO: Update references to disallow "display" (could contain names)


class Condition(Condition):
    # attributes to exclude from the flat representation
    flat_exclusions: ClassVar[set[str]] = (
        "id",
        "meta",
        "implicitRules",
        "language",
        "text",
        "contained",
        "modifierExtension",
        "identifier",
        "verificationStatus",
        "evidence",
        "note",
        "participant",
    )

    # required attributes that are not present in the FHIRflat representation
    flat_defaults: ClassVar[list[str]] = ["clinicalStatus"]

    @classmethod
    def flat_fields(cls) -> list[str]:
        "All fields that are present in the FHIRflat representation"
        return [
            x
            for x in cls.elements_sequence()
            if (x not in cls.flat_exclusions and x not in cls.flat_defaults)
        ]

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

    @property
    def attr_lists(self) -> list[str]:
        """Attributes which take a list of FHIR types."""
        return [
            p.alias
            for p in self.element_properties()
            if "typing.List" in str(p.outer_type_)
        ]

    @classmethod
    def from_flat(cls, file: str) -> Condition | list[Condition]:
        """ "
        Takes a FHIRflat pandas dataframe and populates the resource with the data.

        file: str
            Path to the parquet FHIRflat file containing patient data

        Returns
        -------
        Condition or list[Condition]
        """

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
                            "http://terminology.hl7.org/CodeSystem/"
                            "condition-clinical"
                        ),
                        "code": "unknown",
                    }
                ]
            }

            # find and group keys belonging to the same concept
            grouped_keys = [k for k in data.keys() if "." in k]
            grouped_keys.sort()
            groups = [
                {k: [gs for gs in g]}
                for k, g in groupby(grouped_keys, lambda x: x.split(".")[0])
            ]
            data = expand_concepts(data, groups)

            # create lists for properties which are lists of FHIR types
            # FIXUP: This is not elegant, or fast
            list_fields = [
                p.alias
                for p in cls.element_properties()
                if "typing.List" in str(p.outer_type_)
            ]
            for field in [x for x in data.keys() if x in list_fields]:
                data[field] = [data[field]]

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
            FHIRflat file containing condition data
        """

        # identify attributes that are lists of FHIR types
        list_resources = self.attr_lists

        # clear data from attributes not used in FHIRflat
        for field in [x for x in self.elements_sequence() if x in self.flat_exclusions]:
            setattr(self, field, None)
            list_resources.remove(field) if field in list_resources else None

        flat_df = fhir2flat(self, lists=list_resources)

        # remove required attributes now it's in the flat representation
        for attr in self.flat_defaults:
            flat_df.drop(list(flat_df.filter(regex=attr)), axis=1, inplace=True)

        return flat_df.to_parquet(filename)

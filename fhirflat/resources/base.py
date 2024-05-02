# from pydantic import BaseModel
from __future__ import annotations
from fhir.resources.domainresource import DomainResource

import pandas as pd

from ..fhir2flat import fhir2flat
from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class FHIRFlatBase(DomainResource):

    flat_exclusions: ClassVar[set[str]] = (
        "meta",
        "implicitRules",
        "language",
        "text",
        "contained",
        "modifierExtension",
    )

    flat_defaults: ClassVar[list[str]] = []

    @classmethod
    def attr_lists(cls) -> list[str]:
        """Attributes which take a list of FHIR types."""
        return [
            p.alias
            for p in cls.element_properties()
            if "typing.List" in str(p.outer_type_) or "list" in str(p.outer_type_)
        ]

    @classmethod
    def flat_fields(cls) -> list[str]:
        "All fields that are present in the FHIRflat representation"
        return [x for x in cls.elements_sequence() if x not in cls.flat_exclusions]

    @classmethod
    def cleanup(cls, data: JsonString) -> FHIRFlatBase:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        NotImplementedError("Subclasses must implement this method")

    @classmethod
    def from_flat(cls, file: str) -> FHIRFlatBase | list[FHIRFlatBase]:
        """
        Takes a FHIRflat pandas dataframe and populates the resource with the data.

        file: str
            Path to the parquet FHIRflat file containing patient data
        cleanup: callable
            Function to clean up the data before populating the resource

        Returns
        -------
        FHIRFlatBase or list[FHIRFlatBase]
        """

        df = pd.read_parquet(file)

        df["json_data"] = df.apply(
            lambda row: row.to_json(date_format="iso", date_unit="s"), axis=1
        )
        # Creates a columns of FHIR resource instances
        df["fhir"] = df["json_data"].apply(lambda x: cls.cleanup(x))

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

        # TODO: add support for lists of fhir resources, most likely from a fhir bundle
        # or single file json output.
        # Most likely the input format from FHIR bulk export or for import into FHIR
        # server will be ndjson as referenced in
        # https://build.fhir.org/ig/HL7/bulk-data/export.html.

        # identify attributes that are lists of FHIR types
        list_resources = self.attr_lists()

        # clear data from attributes not used in FHIRflat
        for field in [x for x in self.elements_sequence() if x in self.flat_exclusions]:
            setattr(self, field, None)
            list_resources.remove(field) if field in list_resources else None

        flat_df = fhir2flat(self, lists=list_resources)

        # remove required attributes now it's in the flat representation
        for attr in self.flat_defaults:
            flat_df.drop(list(flat_df.filter(regex=attr)), axis=1, inplace=True)

        return flat_df.to_parquet(filename)

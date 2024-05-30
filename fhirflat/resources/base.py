# from pydantic import BaseModel
from __future__ import annotations
from fhir.resources.domainresource import DomainResource as _DomainResource

import datetime
import pandas as pd
import numpy as np
import orjson

from fhirflat.fhir2flat import fhir2flat
from fhirflat.flat2fhir import expand_concepts

from typing import TypeAlias, ClassVar

JsonString: TypeAlias = str


class FHIRFlatBase(_DomainResource):
    """
    Base class for FHIR resources to add FHIRflat functionality.
    """

    flat_exclusions: ClassVar[set[str]] = {
        "meta",
        "implicitRules",
        "language",
        "text",
        "contained",
        "modifierExtension",
    }

    flat_defaults: ClassVar[list[str]] = []

    backbone_elements: ClassVar[dict] = {}

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
    def cleanup(cls, data: JsonString | dict, json_data=True) -> FHIRFlatBase:
        """
        Load data into a dictionary-like structure, then
        apply resource-specific changes and unpack flattened data
        like codeableConcepts back into structured data.
        """
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def from_flat(cls, file: str) -> FHIRFlatBase | list[FHIRFlatBase]:
        """
        Takes a FHIRflat pandas dataframe and populates the resource with the data.

        Parameters
        ----------
        file: str
            Path to the parquet FHIRflat file containing clinical data

        Returns
        -------
        FHIRFlatBase or list[FHIRFlatBase]
        """

        df = pd.read_parquet(file)

        df["fhir"] = df.apply(
            lambda row: row.to_json(date_format="iso", date_unit="s"), axis=1
        ).apply(lambda x: cls.cleanup(x))

        if len(df) == 1:
            return df["fhir"].iloc[0]
        else:
            return list(df["fhir"])

    @classmethod
    def ingest_backbone_elements(cls, mapped_data: pd.Series) -> pd.Series:
        """
        Unflattens ordered lists of data and forms the correct FHIR format which won't
        be flattened after ingestion (*_dense columns).

        Extends the flat2fhir.expand_concepts function specifically for data ingestion.

        Parameters
        ----------
        mapped_data: pd.Series
            Pandas series of FHIRflat-like dictionaries ready to be converted to FHIR
            format.

        Returns
        -------
        pd.Series

        """

        def fhir_format(row: pd.Series) -> pd.Series:
            for b_e, b_c in cls.backbone_elements.items():
                keys_present = [key for key in row if key.startswith(b_e)]
                if keys_present:
                    condensed_dict = {k: row[k] for k in keys_present}
                    if all(
                        not isinstance(v, list) or len(v) == 1
                        for v in condensed_dict.values()
                    ):
                        continue
                    else:
                        backbone_list = []
                        for i in range(len(next(iter(condensed_dict.values())))):
                            first_item = {
                                k.lstrip(b_e + "."): v[i]
                                for k, v in condensed_dict.items()
                            }
                            backbone_list.append(expand_concepts(first_item, b_c))
                        for k_d in condensed_dict:
                            row.pop(k_d)
                        row[b_e] = backbone_list
            return row

        condensed_mapped_data = mapped_data.apply(fhir_format)
        return condensed_mapped_data

    @classmethod
    def ingest_to_flat(
        cls, data: pd.DataFrame, filename: str, date_format: str, timezone: str
    ):
        """
        Takes a pandas dataframe and populates the resource with the data.
        Creates a FHIRflat parquet file for the resources.

        data: pd.DataFrame
            Pandas dataframe containing the data
        """

        data.loc[:, "flat_dict"] = cls.ingest_backbone_elements(data["flat_dict"])

        # Creates a columns of FHIR resource instances
        data["fhir"] = data["flat_dict"].apply(
            lambda x: cls.cleanup(x, json_data=False)
        )

        # flattens resources back out
        flat_df = data["fhir"].apply(lambda x: x.to_flat())

        # create FHIR expected date format
        for date_cols in [
            x
            for x in flat_df.columns
            if ("date" in x.lower() or "period" in x.lower() or "time" in x.lower())
        ]:
            # replace nan with None
            flat_df[date_cols] = flat_df[date_cols].replace(np.nan, None)

            # convert datetime objects to ISO strings
            # (stops unwanted parquet conversions)
            # but skips over extensions that have floats/strings rather than dates
            flat_df[date_cols] = flat_df[date_cols].apply(
                lambda x: (
                    x.isoformat()
                    if isinstance(x, datetime.datetime) or isinstance(x, datetime.date)
                    else x
                )
            )

        for coding_column in [
            x
            for x in flat_df.columns
            if x.lower().endswith(".code") or x.lower().endswith(".text")
        ]:
            flat_df[coding_column] = flat_df[coding_column].apply(
                lambda x: [x] if isinstance(x, str) else x
            )

        flat_df.to_parquet(f"{filename}.parquet")

    @classmethod
    def fhir_bulk_import(cls, file: str) -> FHIRFlatBase | list[FHIRFlatBase]:
        """
        Takes a ndjson file containing FHIR resources as json strings and returns a
        list of populated FHIR resources.

        Parameters
        ----------
        file: str
            Path to the .ndjson file containing FHIR data

        Returns
        -------
        FHIRFlatBase or list[FHIRFlatBase]
        """

        resources = []
        with open(file, "r") as f:
            for line in f:
                data = orjson.loads(line)
                resources.append(cls(**data))

        if len(resources) == 1:
            return resources[0]
        else:
            return resources

    @classmethod
    def fhir_file_to_flat(cls, source_file: str, output_name: str | None = None):
        """
        Converts a .ndjson file of exported FHIR resources to a FHIRflat parquet file.

        Parameters
        ----------
        source_file: str
            Path to the FHIR resource file.
        output_name: str (optional)
            Name of the parquet file to be generated, optional, defaults to
            {resource}.parquet
        """

        if not output_name:
            output_name = f"{cls.resource_type}.parquet"

        # identify attributes that are lists of FHIR types and not excluded
        list_resources = [x for x in cls.attr_lists() if x not in cls.flat_exclusions]

        fhir_data = cls.fhir_bulk_import(source_file)

        flat_rows = []
        for resource in fhir_data:
            for field in cls.flat_exclusions:
                setattr(resource, field, None)
            flat_rows.append(fhir2flat(resource, lists=list_resources))

        df = pd.concat(flat_rows)

        # remove required attributes now it's in the flat representation
        for attr in cls.flat_defaults:
            df.drop(list(df.filter(regex=attr)), axis=1, inplace=True)

        df.to_parquet(output_name)

    def to_flat(self, filename: str | None = None) -> None | pd.Series:
        """
        Generates a FHIRflat parquet file from the resource.
        If no file name is provided, returns a pandas Series.

        Parameters
        ----------
        filename: str
            Name of the parquet file to be generated.
        """

        # identify attributes that are lists of FHIR types
        list_resources = self.attr_lists()

        # clear data from attributes not used in FHIRflat
        for field in self.flat_exclusions:
            setattr(self, field, None)
            list_resources.remove(field) if field in list_resources else None

        flat_df = fhir2flat(self, lists=list_resources)

        # remove required attributes now it's in the flat representation
        for attr in self.flat_defaults:
            flat_df.drop(list(flat_df.filter(regex=attr)), axis=1, inplace=True)

        if filename:
            flat_df.to_parquet(filename)
        else:
            assert flat_df.shape[0] == 1
            return flat_df.loc[0]

"""
Convert FHIR resources as JSON files to FHIRflat CSV files.
"""

from __future__ import annotations

import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .resources.base import FHIRFlatBase


def flatten_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Takes a column of a dataframe containing dictionaries and flattens it into multiple
    columns.
    """

    i = df.columns.get_loc(column_name)

    expanded_col = pd.json_normalize(df[column_name])
    expanded_col.columns = [
        column_name + "." + str(col) for col in expanded_col.columns
    ]
    df = df.drop(column_name, axis=1)

    new_df = pd.concat([df.iloc[:, :i], expanded_col, df.iloc[:, i:]], axis=1)

    return new_df


def explode_and_flatten(df, list_cols):
    """
    Recursively explodes and flattens a dataframe.
    Columns containing a 'coding' list are left intact for later processing.

    df: flattened fhir resource
    lists: list of columns containing lists in the dataframe
    """
    try:
        df = df.explode([n for n in list_cols])
    except ValueError:
        raise ValueError("Can't explode a dataframe with lists of different lengths")

    if len(df) == 1:
        # only one concept in each list
        for lc in list_cols:
            df = flatten_column(df, lc)
    else:
        raise NotImplementedError("Can't handle lists with more than one concept yet")

    # check if any columns remain containing lists that aren't 'coding' chunks
    list_columns = df.map(lambda x: isinstance(x, list))
    new_list_cols = [
        col
        for col in df.columns
        if (list_columns[col].any() and not col.endswith("coding"))
    ]
    if new_list_cols:
        df = explode_and_flatten(df, new_list_cols)

    return df


def expandCoding(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Turns a column containing a list of dictionaries with coding information into
    2 columns containing a list of strings with the coding information, and the text.

    [ {"system": "http://loinc.org", "code": "1234", "display": "Test"} ]
    becomes
    [ "http://loinc.org/1234" ], ["Test"]

    If a "text" field has already been provided, this overrides the display.
    """

    def expand(
        row: pd.Series, column_name: str, text_present: bool = False
    ) -> pd.Series:
        codes = row[column_name]
        new_codes = []
        new_names = []
        for c in codes:
            if c.get("code") and c.get("system"):
                new_codes.append(c.get("system") + "|" + c.get("code"))
            new_names.append(c.get("display"))

        # empty list if no alphanumeric code is present
        row[column_name] = new_codes
        if not text_present:
            row[column_name.removesuffix(".coding") + ".text"] = new_names
        return row

    text_present = False
    if column_name.removesuffix(".coding") + ".text" in df.columns:
        text_present = True

    df = df.apply(lambda x: expand(x, column_name, text_present), axis=1)

    if not text_present:
        df.insert(
            df.columns.get_loc(column_name) + 1,
            column_name.removesuffix(".coding") + ".text",
            df.pop(column_name.removesuffix(".coding") + ".text"),
        )

    df.rename(
        columns={column_name: column_name.removesuffix(".coding") + ".code"},
        inplace=True,
    )

    return df


def condenseReference(df: pd.DataFrame, reference: str) -> pd.DataFrame:
    """
    Condenses a reference into a string containing the reference type and the reference
    id.

    References are already present as "Patient/f201", so just need to rename the column.
    """
    # if reference is still nested in a dictionary, retrieve it
    ref = df[reference].str["reference"]
    if all(ref.isna()):
        df.rename(
            columns={reference: "".join(reference.rsplit(".reference", 1))},
            inplace=True,
        )
    else:
        df[reference] = ref

    # drop any display text for references, might contain identifying information
    if reference.removesuffix(".reference") + ".display" in df.columns:
        df.drop(columns=reference.removesuffix(".reference") + ".display", inplace=True)
    return df


def condenseSystem(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    For instances of coding not wrapped in a "coding" block, condenses the system and
     code columns into one.
    """
    base_name = col_name.removesuffix(".system")
    df[base_name + ".code"] = df[col_name] + "|" + df[base_name + ".code"]
    df.drop(col_name, axis=1, inplace=True)
    return df


def fhir2flat(resource: FHIRFlatBase, lists: list | None = None) -> pd.DataFrame:
    """
    Converts a FHIR JSON file into a FHIRflat file.

    resource: fhir.resource.Resource
    lists: list
        List of columns that are lists of FHIR concepts that need to be expanded.
    """

    # Flatten JSON and convert to DataFrame
    df = pd.json_normalize(resource.dict())

    if lists:
        list_cols = [n for n in lists if n in df.columns]
        if list_cols:
            df = explode_and_flatten(df, list_cols)

    # expand all instances of the "coding" list
    for coding in df.columns[df.columns.str.endswith("coding")]:
        df = expandCoding(df, coding)

    # condense all references
    for reference in df.columns[df.columns.str.endswith("reference")]:
        df = condenseReference(df, reference)

    # condense any remaining codes not wrapped in a "coding" block
    for col in df.columns[df.columns.str.endswith(".system")]:
        df = condenseSystem(df, col)

    return df

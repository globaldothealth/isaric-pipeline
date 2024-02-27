"""
Convert FHIR resources as JSON files to FHIRflat CSV files.
"""

import pandas as pd
import fhir.resources as fhir


def flatten_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Takes a column of a dataframe containing dictionaries and flattens it into multiple
    columns.
    """

    i = df.columns.get_loc(column_name)

    expanded_col = df[column_name].apply(pd.Series)
    expanded_col.columns = [
        column_name + "." + str(col) for col in expanded_col.columns
    ]
    df = df.drop(column_name, axis=1)

    new_df = pd.concat([df.iloc[:, :i], expanded_col, df.iloc[:, i:]], axis=1)

    return new_df


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
            new_codes.append(c["system"] + "|" + c["code"])
            new_names.append(c.get("display"))

        row[column_name] = new_codes
        if not text_present:
            row[column_name.removesuffix(".coding") + ".text"] = (
                new_names  # FIXUP: doesn't put name next to code
            )
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
    df.rename(columns={reference: reference.replace(".reference", "")}, inplace=True)

    # drop any display text for references, might contain identifying information
    if reference.removesuffix(".reference") + ".display" in df.columns:
        df.drop(columns=reference.removesuffix(".reference") + ".display", inplace=True)
    return df


def fhir2flat(
    resource: fhir.resource.Resource, lists: list | None = None
) -> pd.DataFrame:
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
            try:
                df = df.explode([n for n in list_cols])
            except ValueError:
                raise ValueError("Can't explode lists with more than one concept yet")
            if len(df) == 1:
                # only one concept in each list
                for lc in list_cols:
                    df = flatten_column(df, lc)
            else:
                raise NotImplementedError(
                    "Can't handle lists with more than one concept yet"
                )

    # expand all instances of the "coding" list
    for coding in df.columns[df.columns.str.endswith("coding")]:
        df = expandCoding(df, coding)

    # condense all references
    for reference in df.columns[df.columns.str.endswith("reference")]:
        df = condenseReference(df, reference)

    return df

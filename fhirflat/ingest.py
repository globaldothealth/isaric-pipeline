"""
Stores the main functions for converting clinical data (initally from RedCap-ARCH) to
FHIRflat.
"""

import pandas as pd
import numpy as np
import warnings
import os
from math import isnan
from fhirflat.util import get_local_resource

# 1:1 (single row, single resource) mapping: Patient, Encounter
# 1:M (single row, multiple resources) mapping: Observation, Condition, Procedure, ...

"""
TODO
* sort out how to choose ID's e.g. location within encounter etc
* cope with 'if' statements - e.g. for date overwriting.
* deal with how to check if lists are appropriate when adding multiple values to a
    single field - list options.
* Consider using pandarallel (https://pypi.org/project/pandarallel/) to parallelize
    the apply function, particularly for one to many mappings.
"""


def find_field_value(row, response, mapp, raw_data=None):
    """
    Returns the data for a given field, given the mapping.
    For one to many resources the raw data is provided to allow for searching for other
    fields than in the melted data.
    """
    if mapp == "<FIELD>":
        return response
    elif "+" in mapp:
        mapp = mapp.split("+")
        results = [find_field_value(row, response, m, raw_data) for m in mapp]
        results = [str(x) for x in results if not (isinstance(x, float) and isnan(x))]
        return " ".join(results) if "/" not in results[0] else "".join(results)
    elif "if not" in mapp:
        mapp = mapp.replace(" ", "").split("ifnot")
        results = [find_field_value(row, response, m, raw_data) for m in mapp]
        x, y = results
        if isinstance(y, float):
            return x if isnan(y) else None
        else:
            return x if not y else None
    elif "<" in mapp:
        col = mapp.lstrip("<").rstrip(">")
        try:
            return row[col]
        except KeyError:
            if raw_data is not None:
                try:
                    return raw_data.loc[row["index"], col]
                except KeyError:
                    raise KeyError(f"Column {col} not found in data")
            else:
                raise KeyError(f"Column {col} not found in the filtered data")
    else:
        return mapp


def create_dict_wide(row: pd.Series, map_df: pd.DataFrame) -> dict:
    """
    Takes a wide-format dataframe and iterates through the columns of the row,
    applying the mapping to each column and produces a fhirflat-like dictionary to
    initialize the resource object for each row.
    """

    result = {}
    for column in row.index:
        if column in map_df.index.get_level_values(0):
            response = row[column]
            if pd.notna(response):  # Ensure there is a response to map
                try:
                    # Retrieve the mapping for the given column and response
                    if pd.isna(map_df.loc[column].index).all():
                        mapping = map_df.loc[(column, np.nan)].dropna()
                    else:
                        mapping = map_df.loc[(column, str(int(response)))].dropna()
                    snippet = {
                        k: (
                            v
                            if "<" not in str(v)
                            else find_field_value(row, response, v)
                        )
                        for k, v in mapping.items()
                    }
                except KeyError:
                    # No mapping found for this column and response despite presence
                    # in mapping file
                    warnings.warn(
                        f"No mapping for column {column} response {response}",
                        UserWarning,
                    )
                    continue
            else:
                continue
        else:
            raise ValueError(f"Column {column} not found in mapping file")
        duplicate_keys = set(result.keys()).intersection(snippet.keys())
        if not duplicate_keys:
            result = result | snippet
        else:
            if all(
                result[key] == snippet[key] for key in duplicate_keys
            ):  # Ignore duplicates if they are the same
                continue
            elif all(result[key] is None for key in duplicate_keys):
                result.update(snippet)
            else:
                for key in duplicate_keys:
                    if isinstance(result[key], list):
                        result[key].append(snippet[key])
                    else:
                        result[key] = [result[key], snippet[key]]
    return result


def create_dict_long(
    row: pd.Series, full_df: pd.DataFrame, map_df: pd.DataFrame
) -> dict | None:
    """
    Takes a long-format dataframe and a mapping file, and produces a fhirflat-like
    dictionary for each row in the dataframe.
    """

    column = row["column"]
    response = row["value"]
    if pd.notna(response):  # Ensure there is a response to map
        try:
            # Retrieve the mapping for the given column and response
            if pd.isna(map_df.loc[column].index).all():
                mapping = map_df.loc[(column, np.nan)].dropna()
            else:
                mapping = map_df.loc[(column, str(int(response)))].dropna()
            snippet = {
                k: (
                    v
                    if "<" not in str(v)
                    else find_field_value(row, response, v, raw_data=full_df)
                )
                for k, v in mapping.items()
            }
            return snippet
        except KeyError:
            # No mapping found for this column and response despite presence
            # in mapping file
            warnings.warn(
                f"No mapping for column {column} response {response}",
                UserWarning,
            )
            return None


def create_dictionary(
    data: str,
    map_file: str,
    resource: str,
    one_to_one=False,
    subject_id="subjid",
) -> pd.DataFrame | None:
    """
    Given a data file and a single mapping file for one FHIR resource type,
    returns a single column dataframe with the mapped data in a FHIRflat-like
    format, ready for further processing.

    Parameters
    ----------
    data: str
        The path to the data file containing the clinical data.
    map_file: pd.DataFrame
        The path to the mapping file containing the mapping of the clinical data to the
        FHIR resource.
    resource: str
        The name of the resource being mapped.
    one_to_one: bool
        Whether the resource should be mapped as one-to-one or one-to-many.
    subject_id: str
        The name of the column containing the subject ID in the data file.
    """

    data: pd.DataFrame = pd.read_csv(data, header=0)
    map_df: pd.DataFrame = pd.read_csv(map_file, header=0)

    # setup the data -----------------------------------------------------------
    relevant_cols = map_df["raw_variable"].dropna().unique()
    filtered_data = data.loc[:, data.columns.isin(relevant_cols)].copy()

    if filtered_data.empty:
        warnings.warn(f"No data found for the {resource} resource.", UserWarning)
        return None

    if one_to_one:

        def condense(x):
            """
            In case where data is actually multi-row per subject, condenses the relevant
            data into a single row for 1:1 mapping.
            """

            # Check if the column contains nan values
            if x.isnull().any():
                # If the column contains a single non-nan value, return it
                non_nan_values = x.dropna()
                if non_nan_values.nunique() == 1:
                    return non_nan_values
                elif non_nan_values.empty:
                    return np.nan
                else:
                    raise ValueError("Multiple values found in one-to-one mapping")
            else:
                if len(x) == 1:
                    return x
                else:
                    raise ValueError("Multiple values found in one-to-one mapping")

        filtered_data = filtered_data.groupby(subject_id, as_index=False).agg(condense)

    if not one_to_one:
        filtered_data = filtered_data.reset_index()
        melted_data = filtered_data.melt(id_vars="index", var_name="column")

    # set up the mappings -------------------------------------------------------

    # Fills the na input variables with the previous value
    map_df["raw_variable"] = map_df["raw_variable"].ffill()

    # strips the text answers out of the response column
    map_df["raw_response"] = map_df["raw_response"].apply(
        lambda x: x.split(",")[0] if isinstance(x, str) else x
    )

    # Set multi-index for easier access
    map_df.set_index(["raw_variable", "raw_response"], inplace=True)

    # Generate the flat_like dictionary
    if one_to_one:
        filtered_data["flat_dict"] = filtered_data.apply(
            create_dict_wide, args=[map_df], axis=1
        )
        return filtered_data
    else:
        melted_data["flat_dict"] = melted_data.apply(
            create_dict_long, args=[data, map_df], axis=1
        )
        return melted_data["flat_dict"].to_frame()


def convert_data_to_flat(
    data: str,
    folder_name: str,
    mapping_files_types: tuple[dict, dict] | None = None,
    sheet_id: str | None = None,
    subject_id="subjid",
):
    """
    Takes raw clinical data (currently assumed to be a one-row-per-patient format like
    RedCap exports) and produces a folder of FHIRflat files, one per resource. Takes
    either local mapping files, or a Google Sheet ID containing the mapping files.

    Parameters
    ----------
    data: str
        The path to the raw clinical data file.
    folder_name: str
        The name of the folder to store the FHIRflat files.
    mapping_files_types: tuple[dict, dict] | None
        A tuple containing two dictionaries, one with the mapping files for each
        resource type and one with the mapping type (either one-to-one or one-to-many)
        for each resource type.
    sheet_id: str | None
        The Google Sheet ID containing the mapping files. The first sheet must contain
        the mapping types - one column listing the resource name, and another describing
        whether the mapping is one-to-one or one-to-many. The subsequent sheets must
        be named by resource, and contain the mapping for that resource.
    subject_id: str
        The name of the column containing the subject ID in the data file.
    """

    if not mapping_files_types and not sheet_id:
        raise TypeError("Either mapping_files_types or sheet_id must be provided")

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if mapping_files_types:
        mappings, types = mapping_files_types
    else:
        sheet_link = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        )

        df_types = pd.read_csv(sheet_link, header=0, index_col="Resources")
        types = dict(
            zip(
                df_types.index,
                df_types["Resource Type"],
            )
        )
        sheet_keys = {r: df_types.loc[r, "Sheet ID"] for r in types.keys()}
        mappings = {
            get_local_resource(r): sheet_link + f"&gid={i}"
            for r, i in sheet_keys.items()
        }

    for resource, map_file in mappings.items():

        t = types[resource.__name__]
        if t == "one-to-one":
            df = create_dictionary(
                data,
                map_file,
                resource.__name__,
                one_to_one=True,
                subject_id=subject_id,
            )
            if df is None:
                continue
        elif t == "one-to-many":
            df = create_dictionary(
                data,
                map_file,
                resource.__name__,
                one_to_one=False,
                subject_id=subject_id,
            )
            if df is None:
                continue
            else:
                df = df.dropna().reset_index(drop=True)
        else:
            raise ValueError(f"Unknown mapping type {t}")

        resource.ingest_to_flat(
            df, os.path.join(folder_name, resource.__name__.lower())
        )

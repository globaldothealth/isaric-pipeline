"""
Stores the main functions for converting clinical data (initally from RedCap-ARCH) to
FHIRflat.

Assumes two files are provided: one with the clinical data and one containing the
mappings. PL: Actually, maybe rather than the mappings it's either a file or a
dictionary showing the location of each mapping file (one per resource type).

TODO: Eventually, this should link to a google sheet file that contains the mappings
"""

import pandas as pd
import numpy as np
import warnings

# 1:1 (single row, single resource) mapping: Patient, Encounter
# 1:M (single row, multiple resources) mapping: Observation, Condition, Procedure, ...

"""
TODO
* sort out reference formatting
* cope with 'if' statements - e.g. for date overwriting.
* deal with duplicates/how to add multiple values to a single field - list options.
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
        results = [find_field_value(row, response, m) for m in mapp]
        results = [x for x in results if x == x]
        return " ".join(results)
    else:
        col = mapp.lstrip("<").rstrip(">")
        try:
            return row[col]
        except KeyError:
            return raw_data.loc[row["index"], col]


def create_dict_from_row(row, map_df):
    """
    Iterates through the columns of the row, applying the mapping to each columns
    and produces a fhirflat-like dictionary to initialize the resource object.
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
            else:
                raise ValueError(
                    "Duplicate keys in mapping:"
                    f" {set(result.keys()).intersection(snippet.keys())}"
                )
    return result


def create_dict_from_cell(row, full_df, map_df):
    """
    Iterates through the columns of the row, applying the mapping to each columns
    and produces a fhirflat-like dictionary to initialize the resource object.
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
    data: pd.DataFrame, map_file: pd.DataFrame, one_to_one=False
) -> pd.DataFrame:
    """
    Given a data file and a single mapping file for one FHIR resource type,
    returns a single column dataframe with the mapped data in a FHIRflat-like
    format, ready for further processing.

    Parameters
    ----------
    data: pd.DataFrame
        The data file containing the clinical data.
    map_file: pd.DataFrame
        The mapping file containing the mapping of the clinical data to the FHIR
        resource.
    one_to_one: bool
        Whether the resource should be mapped as one-to-one or one-to-many.
    """

    data = pd.read_csv(data, header=0)
    map_df = pd.read_csv(map_file, header=0)

    # setup the data -----------------------------------------------------------
    relevant_cols = map_df["redcap_variable"].dropna().unique()

    if one_to_one:
        filtered_data = data[relevant_cols].copy()
    else:
        filtered_data = data.loc[:, data.columns.isin(relevant_cols)].reset_index()
        melted_data = filtered_data.melt(id_vars="index", var_name="column")

    # set up the mappings -------------------------------------------------------

    # Fills the na redcap variables with the previous value
    map_df["redcap_variable"] = map_df["redcap_variable"].ffill()

    # strips the text answers out of the redcap_response column
    map_df["redcap_response"] = map_df["redcap_response"].apply(
        lambda x: x.split(",")[0] if isinstance(x, str) else x
    )

    # Set multi-index for easier access
    map_df.set_index(["redcap_variable", "redcap_response"], inplace=True)

    # Generate the flat_like dictionary
    if one_to_one:
        filtered_data["flat_dict"] = filtered_data.apply(
            create_dict_from_row, args=[map_df], axis=1
        )
        return filtered_data
    else:
        melted_data["flat_dict"] = melted_data.apply(
            create_dict_from_cell, args=[data, map_df], axis=1
        )
        return melted_data["flat_dict"].to_frame()


def load_data(data, mapping_files, resource_type, file_name):

    df = create_dictionary(data, mapping_files, one_to_one=True)

    resource_type.ingest_to_flat(df, file_name)


def load_data_one_to_many(data, mapping_files, resource_type, file_name):

    df = create_dictionary(data, mapping_files, one_to_one=False)

    resource_type.ingest_to_flat(df.dropna(), file_name)

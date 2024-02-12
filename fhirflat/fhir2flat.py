"""
Convert FHIR resources as JSON files to FHIRflat CSV files.
"""

import pandas as pd
import fhir.resources as fhir


def fhir2flat(resource: fhir.resource.Resource):
    """
    Converts a FHIR JSON file into a FHIRflat file.

    resource: fhir.resource.Resource
    """

    # Flatten JSON and convert to DataFrame
    df = pd.json_normalize(resource.dict())

    return df

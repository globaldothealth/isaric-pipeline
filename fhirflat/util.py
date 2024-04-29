# Utility functions for FHIRflat
from itertools import groupby
import fhir.resources
import re
import importlib

from .resources import extensions


def group_keys(data_keys: list[str]) -> list[dict[str, list[str]]]:
    """
    Finds columns with a '.' in the name denoting data that has been flattened and
     groups them together.

    ["code.code", "code.text", "value.code", "value.text", "fruitcake"]
    returns
    {"code": ["code.code", "code.text"], "value": ["value.code", "value.text"]}
    """
    grouped_keys = [k for k in data_keys if "." in k]
    grouped_keys.sort()
    groups = {
        k: [gs for gs in g] for k, g in groupby(grouped_keys, lambda x: x.split(".")[0])
    }
    return groups


def get_fhirtype(t: str | list[str]):
    """
    Finds the relevent class from fhir.resources for a given string.
    """

    if isinstance(t, list):
        return [get_fhirtype(x) for x in t]

    if not hasattr(extensions, t):
        try:
            return getattr(getattr(fhir.resources, t.lower()), t)
        except AttributeError:
            file_words = re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", t)
            file = "".join(file_words[:-1]).lower()

            try:
                return getattr(getattr(fhir.resources, file), t)
            except AttributeError:
                try:
                    module = importlib.import_module(f"fhir.resources.{t.lower()}")
                    return getattr(module, t)
                except ImportError or ModuleNotFoundError:
                    # Handle the case where the module does not exist.
                    raise AttributeError(f"Could not find {t} in fhir.resources")

    else:
        return get_local_extension_type(t)


def get_local_extension_type(t: str):
    """
    Finds the relevent class from fhir.resources for a given string.
    """

    try:
        return getattr(extensions, t)
    except AttributeError:
        raise AttributeError(f"Could not find {t} in fhirflat extensions")

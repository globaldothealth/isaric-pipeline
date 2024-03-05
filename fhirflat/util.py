# Utility functions for FHIRflat
from itertools import groupby


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

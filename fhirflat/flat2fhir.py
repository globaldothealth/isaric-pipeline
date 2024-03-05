# Converts FHIRflat files into FHIR resources
from .util import group_keys


def create_codeable_concept(
    old_dict: dict[str, list[str] | str], name: str
) -> dict[str, list[str]]:
    """Re-creates a codeableConcept structure from the FHIRflat representation."""
    codes = old_dict[name + ".code"]
    if len(codes) == 1:
        system, code = codes[0].split("|")
        display = (
            old_dict[name + ".text"][0]
            if isinstance(old_dict[name + ".text"], list)
            else old_dict[name + ".text"]
        )
        new_dict = {"coding": [{"system": system, "code": code, "display": display}]}
    elif not codes:
        display = (
            old_dict[name + ".text"][0]
            if isinstance(old_dict[name + ".text"], list)
            else old_dict[name + ".text"]
        )
        new_dict = {"coding": [{"display": display}]}
    else:
        new_dict = {"coding": []}
        for code, name in zip(codes, old_dict[name + ".text"]):
            system, code = code.split("|")
            display = name

            subdict = {"system": system, "code": code, "display": display}

            new_dict["coding"].append(subdict)

    return new_dict


def createQuantity(df, group):
    quant = {}

    for attribute in df.keys():
        attr = attribute.split(".")[-1]
        if attr == "code":
            system, code = df[group + ".code"].split("|")
            quant["code"] = code
            quant["system"] = system
        else:
            quant[attr] = df[group + "." + attr]

    return quant


def expand_concepts(data: dict) -> dict:
    """
    Combines columns containing flattened FHIR concepts back into
    JSON-like structures.
    """

    groups = group_keys(data.keys())

    expanded = {}
    keys_to_replace = []
    for k, v in groups.items():
        keys_to_replace += v
        v_dict = {k: data[k] for k in v}
        if any([s.count(".") > 1 for s in v]):
            # strip the outside group name
            stripped_dict = {s.split(".", 1)[1]: v_dict[s] for s in v}
            # call recursively
            new_v_dict = expand_concepts(stripped_dict)
            # add outside group key back on
            v_dict = {f"{k}." + old_k: v for old_k, v in new_v_dict.items()}

        if k.endswith("Quantity"):
            expanded[k] = createQuantity(v_dict, k)
        elif k + ".code" in v_dict.keys():
            v = create_codeable_concept(v_dict, k)
            expanded[k] = v
        elif "period" in k.lower():
            v = {"start": data.get(k + ".start"), "end": data.get(k + ".end")}
            expanded[k] = v
        else:
            expanded[k] = {s.split(".", 1)[1]: v_dict[s] for s in v_dict}

    for k in keys_to_replace:
        data.pop(k)
    data.update(expanded)
    return data

# Converts FHIRflat files into FHIR resources


def create_codeable_concept(old_dict: dict[str, list[str] | str], name: str):
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
    else:
        new_dict = {"coding": []}
        for code, name in zip(codes, old_dict[name + ".text"]):
            system, code = code.split("|")
            display = name

            subdict = {"system": system, "code": code, "display": display}

            new_dict["coding"].append(subdict)

    return new_dict


def expand_concepts(data: dict, groups: dict[str, list[str]]):
    """
    Combines columns containing flattened FHIR concepts back into
    JSON-like structures.
    """
    expanded = {}
    keys_to_replace = []
    for pair in groups:
        for k, v in pair.items():
            keys_to_replace += v
            v_dict = {k: data[k] for k in v}
            if k + ".code" in v_dict.keys():
                v = create_codeable_concept(v_dict, k)
                expanded[k] = v

    for k in keys_to_replace:
        data.pop(k)
    data.update(expanded)
    return data

# Converts FHIRflat files into FHIR resources
from .util import group_keys, get_fhirtype, get_local_extension_type
from fhir.resources.quantity import Quantity
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.period import Period
from fhir.resources.fhirprimitiveextension import FHIRPrimitiveExtension
from fhir.resources.datatype import DataType as _DataType
from fhir.resources.domainresource import DomainResource as _DomainResource
from fhir.resources.backbonetype import BackboneType as _BackboneType

from pydantic.v1.error_wrappers import ValidationError


def create_codeable_concept(
    old_dict: dict[str, list[str] | str], name: str
) -> dict[str, list[str]]:
    """Re-creates a codeableConcept structure from the FHIRflat representation."""

    # for reading in from ingestion pipeline
    if name + ".code" in old_dict and name + ".system" in old_dict:
        code = old_dict[name + ".code"]
        if isinstance(code, list) and len(code) > 1:
            new_dict = {"coding": []}
            for system, code, name in zip(
                old_dict[name + ".system"], code, old_dict[name + ".text"]
            ):
                formatted_code = code if isinstance(code, str) else str(int(code))
                display = name

                subdict = {"system": system, "code": code, "display": display}

                new_dict["coding"].append(subdict)
        else:
            formatted_code = code if isinstance(code, str) else str(int(code))
            new_dict = {
                "coding": [
                    {
                        "system": old_dict[name + ".system"],
                        "code": formatted_code,
                        "display": old_dict[name + ".text"],
                    }
                ]
            }
        return new_dict

    # From FHIRflat file
    codes = old_dict.get(name + ".code")

    if codes is None:
        return {
            "text": (
                old_dict[name + ".text"][0]
                if isinstance(old_dict[name + ".text"], list)
                else old_dict[name + ".text"]
            )
        }

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
            if group + ".system" in df.keys():
                # reading in from ingestion pipeline
                quant["code"] = df[group + ".code"]
                quant["system"] = df[group + ".system"]
            else:
                system, code = df[group + ".code"].split("|")
                quant["code"] = code
                quant["system"] = system
        else:
            quant[attr] = df[group + "." + attr]

    return quant


def createExtension(exts: dict):
    """
    Searches through the schema of the extensions to find the correct datatype

    Covers the scenario where there is a list of extensions,e.g.
    [{'type': 'approximateDate'}, {'type': 'relativeDay'}, {'type': 'Extension'}]
    and finds the appropriate class for the data provided.

    Args:
    exts: dict
        e.g. {"relativeDay": 3, "approximateDate": "month 6"}
    """

    extensions = []

    extension_classes = {e: get_local_extension_type(e) for e in exts.keys()}

    for e, v in exts.items():
        properties = extension_classes[e].schema()["properties"]
        data_options = [key for key in properties.keys() if key.startswith("value")]
        if len(data_options) == 1:
            extensions.append({"url": e, data_options[0]: v})
        else:
            for opt in data_options:
                try:
                    extension_classes[e](**{opt: v})
                    extensions.append({"url": e, opt: v})
                    break
                except ValidationError:
                    continue

    return extensions


def set_datatypes(k, v_dict, klass) -> dict:
    if klass == Quantity:
        return createQuantity(v_dict, k)
    elif klass == CodeableConcept:
        return create_codeable_concept(v_dict, k)
    elif klass == Period:
        return {"start": v_dict.get(k + ".start"), "end": v_dict.get(k + ".end")}
    elif issubclass(klass, FHIRPrimitiveExtension):
        return {
            "extension": createExtension(
                {s.split(".", 1)[1]: v_dict[s] for s in v_dict}
            ),
        }
    elif issubclass(klass, _DataType) and not issubclass(klass, _BackboneType):
        # not quite
        prop = klass.schema()["properties"]
        value_type = [key for key in prop.keys() if key.startswith("value")]
        if not value_type:
            # nested extension
            return {
                "url": k,
                "extension": createExtension(
                    {s.split(".", 1)[1]: v_dict[s] for s in v_dict}
                ),
            }

        data_type = prop[value_type[0]]["type"]
        data_class = get_fhirtype(data_type)
        return {"url": k, f"{value_type[0]}": set_datatypes(k, v_dict, data_class)}

    return {s.split(".", 1)[1]: v_dict[s] for s in v_dict}


def expand_concepts(data: dict, data_class: type[_DomainResource]) -> dict:
    """
    Combines columns containing flattened FHIR concepts back into
    JSON-like structures.
    """
    groups = group_keys(data.keys())
    group_classes = {}

    for k in groups.keys():

        if isinstance(data_class, list):
            title_matches = [
                k.lower() == c.schema()["title"].lower() for c in data_class
            ]
            result = [x for x, y in zip(data_class, title_matches) if y]
            if len(result) == 1:
                group_classes[k] = k
                continue
            else:
                raise ValueError(
                    f"Couldn't find a matching class for {k} in {data_class}"
                )

        else:
            k_schema = data_class.schema()["properties"].get(k)

            group_classes[k] = (
                k_schema.get("items").get("type")
                if k_schema.get("items") is not None
                else k_schema.get("type")
            )

            if group_classes[k] is None:
                assert k_schema.get("type") == "array"

                group_classes[k] = [
                    opt.get("type") for opt in k_schema["items"]["anyOf"]
                ]

    group_classes = {k: get_fhirtype(v) for k, v in group_classes.items()}

    expanded = {}
    keys_to_replace = []
    for k, v in groups.items():
        keys_to_replace += v
        v_dict = {k: data[k] for k in v}
        if any([s.count(".") > 1 for s in v]):
            # strip the outside group name
            stripped_dict = {s.split(".", 1)[1]: v_dict[s] for s in v}
            # call recursively
            new_v_dict = expand_concepts(stripped_dict, data_class=group_classes[k])
            # add outside group key back on
            v_dict = {f"{k}." + old_k: v for old_k, v in new_v_dict.items()}

        if all(isinstance(v, dict) for v in v_dict.values()):
            # coming back out of nested recursion
            expanded[k] = {s.split(".", 1)[1]: v_dict[s] for s in v_dict}

        else:
            expanded[k] = set_datatypes(k, v_dict, group_classes[k])

        if isinstance(data_class, list):
            continue
        elif data_class.schema()["properties"][k].get("type") == "array":
            if k == "extension":
                expanded[k] = [v for v in expanded[k].values()]
            else:
                expanded[k] = [expanded[k]]

    dense_cols = {
        k: k.removesuffix("_dense") for k in data.keys() if k.endswith("_dense")
    }
    if dense_cols:
        for old_k, new_k in dense_cols.items():
            data[new_k] = data[old_k]
            del data[old_k]

    for k in keys_to_replace:
        data.pop(k)
    data.update(expanded)
    return data

from __future__ import annotations

from fhir.resources.datatype import DataType as _DataType
from fhir.resources.fhirprimitiveextension import (
    FHIRPrimitiveExtension as _FHIRPrimitiveExtension,
)
from fhir.resources import fhirtypes
from pydantic.v1 import Field, validator, root_validator
from typing import Union, Any

from . import extension_types as et

# --------- extensions ------------------------------


class timingPhase(_DataType):

    resource_type = Field("timingPhase", const=True)

    url = Field("timingPhase", const=True, alias="url")

    valueCodeableConcept: fhirtypes.CodeableConceptType = Field(
        None,
        alias="valueCodeableConcept",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "url",
            "valueCodeableConcept",
        ]


class relativeDay(_DataType):

    resource_type = Field("relativeDay", const=True)

    url = Field("relativeDay", const=True, alias="url")

    valueInteger: fhirtypes.Integer = Field(
        None,
        alias="valueInteger",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "url",
            "valueInteger",
        ]


class relativeStart(_DataType):

    resource_type = Field("relativeStart", const=True)

    url = Field("start", const=True, alias="url")

    valueInteger: fhirtypes.Integer = Field(
        None,
        alias="valueInteger",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "url",
            "valueInteger",
        ]


class relativeEnd(_DataType):

    resource_type = Field("relativeEnd", const=True)

    url = Field("end", const=True, alias="url")

    valueInteger: fhirtypes.Integer = Field(
        None,
        alias="valueInteger",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "url",
            "valueInteger",
        ]


class relativePhase(_DataType):

    resource_type = Field("relativePhase", const=True)

    url = Field("relativePhase", const=True, alias="url")

    extension: list[Union[et.relativeStartType, et.relativeEndType]] = Field(
        None,
        alias="extension",
        title="List of `Extension` items (represented as `dict` in JSON)",
        description="Additional content defined by implementations",
        # if property is element of this resource.
        element_property=True,
        # this trys to match the type of the object to each of the union types
        union_mode="smart",
    )

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        start_count = sum(isinstance(item, relativeStart) for item in extensions)
        end_count = sum(isinstance(item, relativeEnd) for item in extensions)

        if start_count > 1 or end_count > 1:
            raise ValueError("relativeStart and relativeEnd can only appear once.")

        return extensions

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "url",
        ]


class approximateDate(_DataType):

    resource_type = Field("approximateDate", const=True)

    url = Field("approximateDate", const=True, alias="url")

    valueDate: fhirtypes.Date = Field(
        None,
        alias="valueDate",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        # Choice of Data Types. i.e value[x]
        one_of_many="value",
        one_of_many_required=True,
    )

    valueString: fhirtypes.String = Field(
        None,
        alias="valueString",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        # Choice of Data Types. i.e value[x]
        one_of_many="value",
        one_of_many_required=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return ["id", "extension", "url", "valueDate", "valueString"]

    @root_validator(pre=True, allow_reuse=True)
    def validate_one_of_many_1136(cls, values: dict[str, Any]) -> dict[str, Any]:
        """https://www.hl7.org/fhir/formats.html#choice
        A few elements have a choice of more than one data type for their content.
        All such elements have a name that takes the form nnn[x].
        The "nnn" part of the name is constant, and the "[x]" is replaced with
        the title-cased name of the type that is actually used.
        The table view shows each of these names explicitly.

        Elements that have a choice of data type cannot repeat - they must have a
        maximum cardinality of 1. When constructing an instance of an element with a
        choice of types, the authoring system must create a single element with a
        data type chosen from among the list of permitted data types.
        """
        one_of_many_fields = {
            "value": [
                "valueDate",
                "valueString",
            ]
        }
        for prefix, fields in one_of_many_fields.items():
            assert cls.__fields__[fields[0]].field_info.extra["one_of_many"] == prefix
            required = (
                cls.__fields__[fields[0]].field_info.extra["one_of_many_required"]
                is True
            )
            found = False
            for field in fields:
                if field in values and values[field] is not None:
                    if found is True:
                        raise ValueError(
                            "Any of one field value is expected from "
                            f"this list {fields}, but got multiple!"
                        )
                    else:
                        found = True
            if required is True and found is False:
                raise ValueError(f"Expect any of field value from this list {fields}.")

        return values


class Duration(_DataType):

    resource_type = Field("Duration", const=True)

    url = Field("duration", const=True, alias="url")

    valueQuantity: fhirtypes.QuantityType = Field(
        None,
        alias="valueQuantity",
        title="Value of extension",
        description=(
            "Value of extension - must be one of a constrained set of the data "
            "types (see [Extensibility](extensibility.html) for a list)."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from
        ``Extension`` according specification,
        with preserving original sequence order.
        """
        return [
            "id",
            "extension",
            "url",
            "valueQuantity",
        ]


# ------------------- extension types ------------------------------


class dateTimeExtension(_FHIRPrimitiveExtension):
    """
    A G.Health specific extension to the FHIR dateTime type
    Allows dates to be specified as either approximate, and/or number of days relative
    to the current date.
    """

    resource_type = Field("dateTimeExtension", const=True)

    extension: list[
        Union[et.approximateDateType, et.relativeDayType, fhirtypes.ExtensionType]
    ] = Field(
        None,
        alias="extension",
        title="List of `Extension` items (represented as `dict` in JSON)",
        description="Additional content defined by implementations",
        # if property is element of this resource.
        element_property=True,
        # this trys to match the type of the object to each of the union types
        union_mode="smart",
    )

    @validator("extension")
    def validate_extension_contents(cls, extensions):
        approx_date_count = sum(
            isinstance(item, approximateDate) for item in extensions
        )
        rel_day_count = sum(isinstance(item, relativeDay) for item in extensions)

        if approx_date_count > 1 or rel_day_count > 1:
            raise ValueError("approximateDate and relativeDay can only appear once.")

        return extensions

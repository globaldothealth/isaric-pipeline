from __future__ import annotations
from fhir.resources.extension import Extension as _Extension
from fhir.resources.datatype import DataType as _DataType
from fhir.resources.fhirprimitiveextension import (
    FHIRPrimitiveExtension as _FHIRPrimitiveExtension,
)
from fhir.resources import fhirtypes
from pydantic.v1 import Field, validator
from typing import Union


class timingPhase(_DataType):

    resource_type = Field("timingPhase", const=True)

    url: fhirtypes.Uri = Field(
        "timingPhase",
        alias="url",
        title="identifies the meaning of the extension",
        description=(
            "Source of the definition for the extension code - a logical name or a "
            "URL."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

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

    resource_type = Field("relativeDayExtension", const=True)

    url: fhirtypes.Uri = Field(
        "relativeDay",
        alias="url",
        title="identifies the meaning of the extension",
        description=(
            "Source of the definition for the extension code - a logical name or a "
            "URL."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

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

    resource_type = Field("relativeStartExtension", const=True)

    url: fhirtypes.Uri = Field(
        "start",
        alias="url",
        title="identifies the meaning of the extension",
        description=(
            "Source of the definition for the extension code - a logical name or a "
            "URL."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

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

    resource_type = Field("relativeEndExtension", const=True)

    url: fhirtypes.Uri = Field(
        "end",
        alias="url",
        title="identifies the meaning of the extension",
        description=(
            "Source of the definition for the extension code - a logical name or a "
            "URL."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

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

    url: fhirtypes.Uri = Field(
        "relativePhase",
        alias="url",
        title="identifies the meaning of the extension",
        description=(
            "Source of the definition for the extension code - a logical name or a "
            "URL."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

    extension: list[Union[relativeStart, relativeEnd]] = Field(
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

    resource_type = Field("approximateDateExtension", const=True)

    url: fhirtypes.Uri = Field(
        "approximateDate",
        alias="url",
        title="identifies the meaning of the extension",
        description=(
            "Source of the definition for the extension code - a logical name or a "
            "URL."
        ),
        # if property is element of this resource.
        element_property=True,
        element_required=True,
    )

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
            "valueDate",
        ]


class dateTimeExtension(_FHIRPrimitiveExtension):
    """
    A G.Health specific extension to the FHIR dateTime type
    Allows dates to be specified as either approximate, and/or number of days relative
    to the current date.
    """

    resource_type = Field("dateTimeExtension", const=True)

    extension: list[Union[approximateDate, relativeDay, _Extension]] = Field(
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


class timingPhaseExtension(_FHIRPrimitiveExtension):
    """
    A G.Health specific extension to the FHIR dateTime type
    Allows dates to be specified as either approximate, and/or number of days relative
    to the current date.
    """

    resource_type = Field("timingPhaseExtension", const=True)

    extension: list[Union[timingPhase, _Extension]] = Field(
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
        phase_count = sum(isinstance(item, timingPhase) for item in extensions)

        if phase_count > 1:
            raise ValueError("timingPhase can only appear once.")

        return extensions


class relativePhaseExtension(_FHIRPrimitiveExtension):
    """
    A G.Health specific extension to the FHIR dateTime type
    Allows dates to be specified as either approximate, and/or number of days relative
    to the current date.
    """

    resource_type = Field("relativePhaseExtension", const=True)

    extension: list[Union[relativePhase, _Extension]] = Field(
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
        phase_count = sum(isinstance(item, relativePhase) for item in extensions)

        if phase_count > 1:
            raise ValueError("relativePhase can only appear once.")

        return extensions

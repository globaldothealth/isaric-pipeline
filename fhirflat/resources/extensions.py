from fhir.resources.extension import Extension as _Extension
from fhir.resources.datatype import DataType as _DataType
from fhir.resources.core import fhirabstractmodel
from fhir.resources import fhirtypes
from pydantic.v1 import Field, root_validator, validator
from pydantic.v1.error_wrappers import ErrorWrapper, ValidationError
from pydantic.v1.errors import MissingError
import typing
from typing import Union


class eventPhase(_DataType):

    resource_type = Field("eventPhaseExtension", const=True)

    url: fhirtypes.Uri = Field(
        "eventPhase",
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


class dateTimeExtension(fhirabstractmodel.FHIRAbstractModel):
    """
    A G.Health specific extension to the FHIR dateTime type
    Allows dates to be specified as either approximate, and/or number of days relative
    to the current date.
    """

    resource_type = Field("dateTimeExtension", const=True)

    id: fhirtypes.String = Field(
        None,
        alias="id",
        title="Type `String`",
        description="Unique id for inter-element referencing",
        # if property is element of this resource.
        element_property=False,
    )

    extension: typing.List[Union[approximateDate, relativeDay, _Extension]] = Field(
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

    @root_validator(pre=True)
    def validate_extension_or_fhir_comment_required(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """Conditional Required Validation"""
        errors = list()
        extension = values.get("extension", None)
        fhir_comments = values.get("fhir_comments", None)

        if (
            values.get("id", None) is None
            and extension is None
            and fhir_comments is None
        ):
            errors.append(ErrorWrapper(MissingError(), loc="extension"))
            raise ValidationError(errors, cls)  # type: ignore

        return values

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``FHIRPrimitiveExtension`` according
        specification, with preserving original sequence order.
        """
        return ["id", "extension"]


class phaseExtension(fhirabstractmodel.FHIRAbstractModel):
    """
    A G.Health specific extension to the FHIR dateTime type
    Allows dates to be specified as either approximate, and/or number of days relative
    to the current date.
    """

    resource_type = Field("phaseExtension", const=True)

    id: fhirtypes.String = Field(
        None,
        alias="id",
        title="Type `String`",
        description="Unique id for inter-element referencing",
        # if property is element of this resource.
        element_property=False,
    )

    extension: typing.List[Union[eventPhase, _Extension]] = Field(
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
        phase_count = sum(isinstance(item, approximateDate) for item in extensions)

        if phase_count > 1:
            raise ValueError("eventPhase can only appear once.")

        return extensions

    @root_validator(pre=True)
    def validate_extension_or_fhir_comment_required(
        cls, values: typing.Dict[str, typing.Any]
    ) -> typing.Dict[str, typing.Any]:
        """Conditional Required Validation"""
        errors = list()
        extension = values.get("extension", None)
        fhir_comments = values.get("fhir_comments", None)

        if (
            values.get("id", None) is None
            and extension is None
            and fhir_comments is None
        ):
            errors.append(ErrorWrapper(MissingError(), loc="extension"))
            raise ValidationError(errors, cls)  # type: ignore

        return values

    @classmethod
    def elements_sequence(cls):
        """returning all elements names from ``FHIRPrimitiveExtension`` according
        specification, with preserving original sequence order.
        """
        return ["id", "extension"]

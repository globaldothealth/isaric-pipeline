from __future__ import annotations
from fhir.resources.fhirtypes import AbstractType as _AbstractType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic.v1.types import CallableGenerator


class AbstractType(_AbstractType):
    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        from . import extension_validators as validators

        yield getattr(validators, cls.__resource_type__.lower() + "_validator")


class timingPhaseType(AbstractType):
    __resource_type__ = "timingPhase"


class relativeDayType(AbstractType):
    __resource_type__ = "relativeDay"


class relativeStartType(AbstractType):
    __resource_type__ = "relativeStart"


class relativeEndType(AbstractType):
    __resource_type__ = "relativeEnd"


class relativePeriodType(AbstractType):
    __resource_type__ = "relativePeriod"


class approximateDateType(AbstractType):
    __resource_type__ = "approximateDate"


class durationType(AbstractType):
    __resource_type__ = "Duration"


class ageType(AbstractType):
    __resource_type__ = "Age"


class birthSexType(AbstractType):
    __resource_type__ = "birthSex"


class dateTimeExtensionType(AbstractType):
    __resource_type__ = "dateTimeExtension"

import pandas as pd
from pandas.testing import assert_frame_equal
import os
from fhirflat.resources.researchsubject import ResearchSubject
import datetime

SUBJECT_DICT_INPUT = {
    "resourceType": "ResearchSubject",
    "id": "example-crossover-placebo-to-drug",
    "identifier": [{"value": "ecsr45"}],
    "status": "active",
    "progress": [
        # {
        #     "type": {
        #         "coding": [
        #             {
        #                 "system": "http://terminology.hl7.org/CodeSystem/research-subject-state-type", # noqa:E501
        #                 "code": "Enrollment",
        #             }
        #         ],
        #         "text": "Enrollment status",
        #     }
        # },
        {
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/research-subject-state-type",  # noqa:E501
                        "code": "Enrollment",
                    }
                ],
                "text": "Enrollment status",
            },
            "subjectState": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/research-subject-state",  # noqa:E501
                        "code": "on-study",
                    }
                ],
                "text": "On-study",
            },
            "reason": {
                "coding": [{"code": "informedConsentSigned"}],
                "text": "Informed consent signed",
            },
            "startDate": "2022-06-10",
        },
    ],
    "period": {"start": "2022-06-10"},
    "study": {"reference": "ResearchStudy/example-ctgov-study-record"},
    "subject": {"reference": "Patient/cfsb1676546565857"},
    "assignedComparisonGroup": "placebo",
    "actualComparisonGroup": "ap303",
}

SUBJECT_FLAT = {
    "resourceType": "ResearchSubject",
    "progress.startDate": datetime.date(2022, 6, 10),
    "progress.type.code": "http://terminology.hl7.org/CodeSystem/research-subject-state-type|Enrollment",  # noqa:E501
    "progress.type.text": "Enrollment status",
    "progress.subjectState.code": "http://terminology.hl7.org/CodeSystem/research-subject-state|on-study",  # noqa:E501
    "progress.subjectState.text": "On-study",
    "progress.reason.code": [[]],  # no system, so no code
    "progress.reason.text": "Informed consent signed",
    "assignedComparisonGroup": "placebo",
    "actualComparisonGroup": "ap303",
    "period.start": datetime.date(2022, 6, 10),
    "study": "ResearchStudy/example-ctgov-study-record",
    "subject": "Patient/cfsb1676546565857",
}

SUBJECT_DICT_OUT = {
    "resourceType": "ResearchSubject",
    "status": "active",
    "progress": [
        {
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/research-subject-state-type",  # noqa:E501
                        "code": "Enrollment",
                        "display": "Enrollment status",
                    }
                ],
            },
            "subjectState": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/research-subject-state",  # noqa:E501
                        "code": "on-study",
                        "display": "On-study",
                    }
                ],
            },
            "reason": {
                "coding": [{"display": "Informed consent signed"}],
            },
            "startDate": "2022-06-10T00:00:00",
        },
    ],
    "period": {"start": "2022-06-10T00:00:00"},
    "study": {"reference": "ResearchStudy/example-ctgov-study-record"},
    "subject": {"reference": "Patient/cfsb1676546565857"},
    "assignedComparisonGroup": "placebo",
    "actualComparisonGroup": "ap303",
}


def test_researchsubject_to_flat():
    sub = ResearchSubject(**SUBJECT_DICT_INPUT)

    sub.to_flat("test_researchsubject.parquet")

    assert_frame_equal(
        pd.read_parquet("test_researchsubject.parquet"),
        pd.DataFrame(SUBJECT_FLAT, index=[0]),
        # Date types are off otherwise, pyarrow uses pytz and pandas uses dateutil
        check_dtype=False,
    )
    os.remove("test_researchsubject.parquet")


def test_researchsubject_from_flat():
    sub = ResearchSubject(**SUBJECT_DICT_OUT)

    flat_sub = ResearchSubject.from_flat("tests/data/researchsubject_flat.parquet")

    assert sub == flat_sub

# ISARIC 3.0 Pipeline

Repository for the ISARIC 3.0 Pipeline project.

## FHIRflat

The ISARIC 3.0 fhir resources are derived from the [fhir.resources](https://github.com/nazrulworld/fhir.resources) package.

FHIR resources can be initialised using a data dictionary
```
from fhir.resources.patient import Patient
data= {
    "id": "f001",
    "name": [{"text": "Micky Mouse"}],
    "gender": "male",
    "deceasedBoolean": False,
    "address": [{"country": "Switzerland"}],
    "birthDate": "1996-05-30",
}
patient = Patient(**data)
```

or in bulk from a FHIR export as an .ndjson file.
```
from fhir.resources.patient import Patient

patients = Patient.fhir_bulk_import("patient_export.ndjson")
```

### To FHIRflat
Once initialised, FHIR resources can be transformed to FHIRflat files using the `to_flat()` function like this
```
patient.to_flat("patient_flat.parquet")
```
which will produce a [parquet file](https://towardsdatascience.com/demystifying-the-parquet-file-format-13adb0206705) which can be read in pandas, producing a dataframe with the following structure
| resourceType | id   | gender | birthDate  | deceasedBoolean |
|--------------|------|--------|------------|-----------------|
| Patient      | f001 | male   | 1996-05-30 | False           |

or a FHIRflat file can be generated directly from a FHIR .ndjson export file.
```
from fhir.resources.patient import Patient

patients = Patient.fhir_to_flat("patient_export.ndjson")
```
This first initialises a Patient data class for each row to make use of the Pydantic 
data validation, then creates a FHIRflat file.

### From FHIRflat
FHIR resources can also be created directly from FHIRflat files
```
Patient.from_flat("patient_flat.parquet")
```
which will return either a single Patient resource, or a list of Patient resources if 
the Parquet file contains multiple rows of data.

### Specification

The FHIRflat structure closely follows that of FHIR, and simply flattens nested columns
in a manner similar to `pd.json_normalize()`. Some fields are excluded either because they are simply used for convenience within a FHIR server, because they contain information not relevant within ISARIC clinical data, or because they would contain Personally identifiable information (PII). These fields can be accessed and edited for each resource using the `flat_exclusions` property. There are a few specifics to FHIRflat that differ from simply normalising a FHIR structure, noted below.

1. **codeableConcepts**

    CodeableConcepts are converted into 2 lists, one of codes and one of the corresponding text. The coding is compressed into a single string with the format `system|code`. The ‘|’ symbol was chosen as it is the standard way to query codes in FHIR servers [(example)](https://www.hl7.org/fhir/search.html#3.2.1.5.5.1.3). Thus a JSON snippet containing a codebleConcept:
    ```
        "code": {
            "coding": [
                        [
                            {
                                "system": "http://loinc.org",
                                "code": "3141-9",
                                "display": "Body weight Measured",
                            },
                            {
                                "system": "http://snomed.info/sct",
                                "code": "27113001",
                                "display": "Body weight",
                            },
                        ]
                    ]
                }
    ```
    is coded as two fields
    | code.code                                                        | code.text                               |
    |------------------------------------------------------------------|-----------------------------------------|
    | ["http://loinc.org\|3141-9", "http://snomed.info/sct\|27113001"] | ["Body weight Measured", "Body weight"] |

    Note that the external `coding` label is removed.

2. **References**

    Reference are a string with the name of the resource with the ID, separated by a forward slash.
    ```
    "subject": {
        "reference": "Patient/f001",
        "display": "Donald Duck"
        }
    ```
    becomes 
    | subject.reference |
    |-------------------|
    |"Patient/f001"     |

    The display text will not be converted due to the risk of revealing identifying information (e.g., a patient's name).

3. **Extensions**

    The base FHIR schema can be extented to meet the needs of individual implementations using extension fields. FHIRflat displays these with the extension `url` as part of the column name. For example

    ```
    "extension": [
        {
            "url": "timingPhase",
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": 278307001,
                        "display": "on admission",
                    }
                ]
            },
        },
        {
            "url": "relativePeriod",
            "extension": [
                {"url": "relativeStart", "valueInteger": 2},
                {"url": "relativeEnd", "valueInteger": 5},
            ],
        },
    ]
    ```
    becomes
    | extension.timingPhase.code          | extension.timingPhase.text | extension.relativePeriod.relativeStart | extension.relativePeriod.relativeEnd |
    |-------------------------------------|----------------------------|----------------------------------------|--------------------------------------|
    | "http://snomed.info/sct\|278307001" | "on admission"             | 2                                      | 5                                    |

    Complex (nested) extensions such as relativePeriod also omit the internal `extension` labels.


3. **0..\* cardinality fields**

    Fields which can contain an unspecified number of duplicate entries are dealt with according to the number of entries present. lists of length == 1 are expanded out as above, while any longer lists are kept in a single column with the data in it's original nested structure and `_dense` appended to the end of the field name. These fields are not expected to be queried regularly in standard analyses.

    For example, the `diagnosis` field of the [Encounter](https://hl7.org/fhir/encounter.html) resource has 0..* cardinality. If a single diagnosis is present, the field is expanded out:
    ```
    "diagnosis": [
        {
            "condition": [{"reference": {"reference": "Condition/stroke"}}],
            "use": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                            "code": "AD",
                            "display": "Admission diagnosis",
                        }
                    ]
                }
            ],
        }
    ]
    ```
    becomes
    | diagnosis.condition.reference | diagnosis.use.code                                         | diagnosis.use.text  |
    |-------------------------------|------------------------------------------------------------|---------------------|
    | Condition/stroke              | "http://terminology.hl7.org/CodeSystem/diagnosis-role\|AD" | Admission diagnosis |

    whereas if 2 different diagnoses are present
    ```
    "diagnosis": [
        {
            "condition": [{"reference": {"reference": "Condition/stroke"}}],
            "use": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                            "code": "AD",
                            "display": "Admission diagnosis",
                        }
                    ]
                }
            ],
        },
        {
            "condition": [{"reference": {"reference": "Condition/f201"}}],
            "use": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                            "code": "DD",
                            "display": "Discharge diagnosis",
                        }
                    ]
                }
            ],
        },
    ]
    ```
    becomes 
    | encounter.diagnosis_dense            |
    |--------------------------------------|
    |"[{"condition": [{"reference"...}]}]" |
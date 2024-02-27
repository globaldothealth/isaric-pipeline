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

### To FHIRflat
Once initialised, FHIR resources can be transformed to FHIRflat files using the `to_flat()` function like this
```
patient.to_flat("patient_flat.parquet")
```
which will produce a [parquet file](https://towardsdatascience.com/demystifying-the-parquet-file-format-13adb0206705) which can be read in pandas, producing a dataframe with the following structure
| resourceType | id   | gender | birthDate  | deceasedBoolean |
|--------------|------|--------|------------|-----------------|
| Patient      | f001 | male   | 1996-05-30 | False           |

### From FHIRflat
FHIR resources can also be created directly from FHIRflat files
```
Patient.from_flat("patient_flat.parquet")
```
which will return either a single Patient resource, or a list of Patient resources.
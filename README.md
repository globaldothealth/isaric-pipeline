# FHIRflat

fhirflat is a library for transforming FHIR resources in NDJSON or native Python
dictionaries to a flat structure that can be written to a Parquet file.

fhirflat is a **prototype library**, subject to **major revisions** that is used
for the [ISARIC](https://isaric.org) 3.0 project and data pipelines. Portions of
the code are specific to the ISARIC project, such as ISARIC specific FHIR
extensions.

For more information, howtos and tutorials, see the
[**documentation**](https://fhirflat.readthedocs.io).

## Installing

You can use `pip` to install `fhirflat`:
```
pip install git+https://github.com/globaldothealth/fhirflat
```

If you are using `requirements.txt`, then add this to your file and rerun `pip
install -r requirements.txt`:
```
https://github.com/globaldothealth/fhirflat/main.tar.gz
```
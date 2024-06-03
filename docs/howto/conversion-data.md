# How to convert clinical data into FHIRflat

fhirflat can be used from the command line, if you wish solely to transform your raw
data into FHIRflat files, or as a python library.

## Command line

```bash
fhirflat transform data-file google-sheet-id date-format timezone-name
```

Here *data-file* data file that fhirflat will transform, and *google-sheet-id* is the unique
ID of the google sheet containing the mapping information (found in the url; the format
if usually https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}, 
you want the spreadsheet_id. The sheet has to be public, i.e. share settings must be set
to 'Anyone with the link' for this to work). *date-format* is the format dates follow in
the raw data, e.g. a "2020-04-20" date has a date format of "%Y-%m-%d", and *timezone*
is the time zone the data was recorded in, e.g. "America/New_York". A full list of 
timezones can be found [here](https://nodatime.org/timezones).

Further information on the structure of the mapping file can be found 
[in the specification](../spec/mapping.md)

## Library

The equivalent function to the CLI described above can be used as

```
fhirflat.convert_data_to_flat("data_file_path", "sheet_id", "%Y-%m-%d", "Brazil/East")
```

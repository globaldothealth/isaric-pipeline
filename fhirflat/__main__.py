import sys

from .ingest import main as ingest_to_flat


def main():
    if len(sys.argv) < 2:
        print(
            """fhirflat: specify subcommand to run

                Available subcommands:
                transform - Convert raw data into FHIRflat files
            """
        )
        sys.exit(1)
    subcommand = sys.argv[1]
    if subcommand not in ["transform"]:
        print("fhirflat: unrecognised subcommand", subcommand)
        sys.exit(1)
    sys.argv = sys.argv[1:]
    if subcommand == "transform":
        ingest_to_flat()
    else:
        pass


if __name__ == "__main__":
    main()

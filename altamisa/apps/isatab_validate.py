# -*- coding: utf-8 -*-
"""Read from ISA-Tab and print validation warnings, if any.
"""

import argparse
import os
import sys
import warnings

from altamisa.isatab import (
    AssayReader,
    AssayValidator,
    InvestigationReader,
    InvestigationValidator,
    StudyReader,
    StudyValidator,
)


def run(args):
    # Show all warnings of same type and content
    if args.show_duplicate_warnings:
        warnings.simplefilter("always")

    # Collect warnings
    with warnings.catch_warnings(record=True) as records:
        run_warnings_caught(args)

    # Print warnings
    for record in records:
        warnings.showwarning(
            record.message, record.category, record.filename, record.lineno, record.line
        )


def run_warnings_caught(args):
    # Read investigation
    investigation = InvestigationReader.from_stream(args.input_investigation_file).read()
    args.input_investigation_file.close()

    # Validate investigation
    InvestigationValidator(investigation).validate()

    # Read studies and assays
    path_in = os.path.normpath(os.path.dirname(args.input_investigation_file.name))
    studies = {}
    assays = {}
    for s, study_info in enumerate(investigation.studies):
        if study_info.info.path:
            with open(os.path.join(path_in, study_info.info.path), "rt") as inputf:
                studies[s] = StudyReader.from_stream("S{}".format(s + 1), inputf).read()
        if study_info.assays:
            assays[s] = {}
        for a, assay_info in enumerate(study_info.assays):
            if assay_info.path:
                with open(os.path.join(path_in, assay_info.path), "rt") as inputf:
                    assays[s][a] = AssayReader.from_stream(
                        "S{}".format(s + 1), "A{}".format(a + 1), inputf
                    ).read()

    # Validate studies and assays
    for s, study_info in enumerate(investigation.studies):
        if study_info.info.path:
            StudyValidator(investigation, study_info, studies[s]).validate()
        for a, assay_info in enumerate(study_info.assays):
            if assay_info.path:
                AssayValidator(
                    investigation, study_info, assay_info, assays[s][a], studies[s]
                ).validate()


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input-investigation-file",
        required=True,
        type=argparse.FileType("rt"),
        help="Path to input investigation file",
    )
    parser.add_argument(
        "--show-duplicate-warnings",
        dest="show_duplicate_warnings",
        action="store_true",
        help=(
            "Show duplicated warnings, i.e. with same message and same category (False by default)"
        ),
    )
    parser.set_defaults(no_warnings=False)

    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

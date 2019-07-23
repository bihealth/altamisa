# -*- coding: utf-8 -*-
"""Read from ISA-Tab and directly write to ISA-Tab.
"""

import argparse
import os
import sys
import warnings

from altamisa.isatab import (
    AssayReader,
    AssayValidator,
    AssayWriter,
    InvestigationReader,
    InvestigationValidator,
    InvestigationWriter,
    StudyReader,
    StudyValidator,
    StudyWriter,
)
from altamisa.exceptions import IsaException


def run(args):
    # Collect warnings
    with warnings.catch_warnings(record=True) as records:
        run_warnings_caught(args)

    # Print warnings
    if not args.no_warnings:
        for record in records:
            warnings.showwarning(
                record.message, record.category, record.filename, record.lineno, record.line
            )


def run_warnings_caught(args):
    # Check if input and output directory are different
    path_in = os.path.realpath(os.path.dirname(args.input_investigation_file))
    path_out = os.path.realpath(os.path.dirname(args.output_investigation_file))
    if path_in == path_out:
        tpl = "Can't output ISA-tab files to same directory as as input: {} == {}"
        msg = tpl.format(path_in, path_out)
        raise IsaException(msg)

    if args.input_investigation_file == "-":  # pragma: no cover
        args.input_investigation_file = sys.stdin
    else:
        args.input_investigation_file = open(args.input_investigation_file, "rt")
    if args.output_investigation_file == "-":  # pragma: no cover
        args.output_investigation_file = sys.stdout
    else:
        args.output_investigation_file = open(args.output_investigation_file, "wt")

    investigation, studies, assays = run_reading(args, path_in)
    run_writing(args, path_out, investigation, studies, assays)


def run_reading(args, path_in):
    # Read investigation
    investigation = InvestigationReader.from_stream(args.input_investigation_file).read()

    # Validate investigation
    InvestigationValidator(investigation).validate()

    # Read studies and assays
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
                AssayValidator(investigation, study_info, assay_info, assays[s][a]).validate()

    return investigation, studies, assays


def run_writing(args, path_out, investigation, studies, assays):
    # Write investigation
    if args.output_investigation_file.name == "<stdout>":
        InvestigationWriter.from_stream(
            investigation, args.output_investigation_file, quote=args.quotes
        ).write()
    else:
        with open(args.output_investigation_file.name, "wt", newline="") as outputf:
            InvestigationWriter.from_stream(investigation, outputf, quote=args.quotes).write()

    # Write studies and assays
    for s, study_info in enumerate(investigation.studies):
        if args.output_investigation_file.name == "<stdout>":
            if study_info.info.path:
                StudyWriter.from_stream(
                    studies[s], args.output_investigation_file, quote=args.quotes
                ).write()
            for a, assay_info in enumerate(study_info.assays):
                if assay_info.path:
                    AssayWriter.from_stream(
                        assays[s][a], args.output_investigation_file, quote=args.quotes
                    ).write()
        else:
            if study_info.info.path:
                with open(
                    os.path.join(path_out, study_info.info.path), "wt", newline=""
                ) as outputf:
                    StudyWriter.from_stream(studies[s], outputf, quote=args.quotes).write()
            for a, assay_info in enumerate(study_info.assays):
                if assay_info.path:
                    with open(os.path.join(path_out, assay_info.path), "wt", newline="") as outputf:
                        AssayWriter.from_stream(assays[s][a], outputf, quote=args.quotes).write()


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--input-investigation-file",
        required=True,
        type=str,
        help="Path to input investigation file",
    )
    parser.add_argument(
        "-o",
        "--output-investigation-file",
        default="-",
        type=str,
        help=(
            'Path to output investigation file, stdout ("-") by default. '
            "Needs to be in a different directory!"
        ),
    )
    parser.add_argument(
        "-q",
        "--quotes",
        default=None,
        type=str,
        help='Character for quoting, e.g. "\\"" (None by default)',
    )
    parser.add_argument(
        "--no-warnings",
        dest="no_warnings",
        action="store_true",
        help="Suppress ISA-tab related warnings (False by default)",
    )
    parser.set_defaults(no_warnings=False)

    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

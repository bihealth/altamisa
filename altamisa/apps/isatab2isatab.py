# -*- coding: utf-8 -*-
"""Read from ISA-Tab and directly write to ISA-Tab.
"""

import argparse
import os
import sys

from altamisa.isatab import (
    AssayReader,
    AssayWriter,
    InvestigationReader,
    InvestigationWriter,
    StudyReader,
    StudyWriter,
)
from altamisa.exceptions import IsaException


def run(args):
    # Check if input and output directory are different
    path_in = os.path.normpath(os.path.dirname(args.input_investigation_file.name))
    path_out = os.path.normpath(os.path.dirname(args.output_investigation_file.name))
    if path_in == path_out:
        tpl = "Can't output ISA-tab files to same directory as as input: {} == {}"
        msg = tpl.format(path_in, path_out)
        raise IsaException(msg)

    # Read investigation
    investigation = InvestigationReader.from_stream(args.input_investigation_file).read()

    # Read studies and assays
    studies = {}
    assays = {}
    for s, study_info in enumerate(investigation.studies):
        with open(os.path.join(path_in, study_info.info.path), "rt") as inputf:
            studies[s] = StudyReader.from_stream(
                investigation, study_info, "S{}".format(s + 1), inputf
            ).read()
        if study_info.assays:
            assays[s] = {}
        for a, assay_info in enumerate(study_info.assays.values()):
            with open(os.path.join(path_in, assay_info.path), "rt") as inputf:
                assays[s][a] = AssayReader.from_stream(
                    investigation,
                    study_info,
                    assay_info,
                    "S{}".format(s + 1),
                    "A{}".format(a + 1),
                    inputf,
                ).read()

    # TODO: independent validation should go here

    # Write investigation
    InvestigationWriter.from_stream(
        investigation, args.output_investigation_file, args.quotes
    ).write()

    # Write studies and assays
    for s, study_info in enumerate(investigation.studies):
        if args.output_investigation_file.name == "<stdout>":
            StudyWriter.from_stream(
                studies[s], args.output_investigation_file, study_info.factors
            ).write()
            for a, assay_info in enumerate(study_info.assays.values()):
                AssayWriter.from_stream(
                    assays[s][a], args.output_investigation_file, study_info.factors
                ).write()
        else:
            with open(os.path.join(path_out, study_info.info.path), "wt") as outputf:
                StudyWriter.from_stream(studies[s], outputf, study_info.factors).write()
            for a, assay_info in enumerate(study_info.assays.values()):
                with open(os.path.join(path_out, assay_info.path), "wt") as outputf:
                    AssayWriter.from_stream(assays[s][a], outputf, study_info.factors).write()


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
        "-o",
        "--output-investigation-file",
        default="-",
        type=argparse.FileType("wt"),
        help=(
            'Path to output investigation file, stdout ("-") by default. '
            "Needs to be in a different directory!"
        ),
    )
    parser.add_argument(
        "-q", "--quotes", default=None, type=str, help="Character for quoting (None by default)"
    )

    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())

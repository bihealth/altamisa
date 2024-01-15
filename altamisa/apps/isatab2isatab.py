# -*- coding: utf-8 -*-
"""Read from ISA-Tab and directly write to ISA-Tab.
"""

from contextlib import ExitStack
import os
import sys
import typing
from typing import Dict, Optional, Tuple
import warnings

import attrs
import typer
from typing_extensions import Annotated

from altamisa.exceptions import IsaException
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
from altamisa.isatab.models import Assay, InvestigationInfo, Study

#: Typer application instance.
app = typer.Typer()


@attrs.define
class Arguments:
    input_investigation_file: str
    output_investigation_file: str
    quotes: Optional[str]
    warnings: bool


def run(args: Arguments):
    # Collect warnings
    with warnings.catch_warnings(record=True) as records:
        run_warnings_caught(args)

    # Print warnings
    if args.warnings:
        for record in records:
            warnings.showwarning(
                record.message,
                record.category,
                record.filename,
                lineno=record.lineno,
                line=record.line,
            )


def run_warnings_caught(args: Arguments):
    # Check if input and output directory are different
    path_in = os.path.realpath(os.path.dirname(args.input_investigation_file))
    path_out = os.path.realpath(os.path.dirname(args.output_investigation_file))
    if path_in == path_out:
        tpl = "Can't output ISA-tab files to same directory as as input: {} == {}"
        msg = tpl.format(path_in, path_out)
        raise IsaException(msg)

    with ExitStack() as stack:
        if args.output_investigation_file == "-":  # pragma: no cover
            output_investigation_file = sys.stdout
        else:
            output_investigation_file = stack.push(open(args.output_investigation_file, "wt"))

        investigation, studies, assays = run_reading(args, path_in)
        run_writing(
            args,
            path_out,
            output_investigation_file,
            investigation,
            studies,
            assays,
        )


def run_reading(
    args, path_in
) -> Tuple[InvestigationInfo, Dict[int, Study], Dict[int, Dict[int, Assay]]]:
    # Read investigation
    with open(args.input_investigation_file, "rt") as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()

    # Validate investigation
    InvestigationValidator(investigation).validate()

    # Read studies and assays
    studies: Dict[int, Study] = {}
    assays: Dict[int, Dict[int, Assay]] = {}
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


def run_writing(
    args,
    path_out,
    output_investigation_file: typing.TextIO,
    investigation: InvestigationInfo,
    studies: Dict[int, Study],
    assays: Dict[int, Dict[int, Assay]],
):
    # Write investigation
    if output_investigation_file.name == "<stdout>":
        InvestigationWriter.from_stream(
            investigation, output_investigation_file, quote=args.quotes
        ).write()
    else:
        with open(output_investigation_file.name, "wt", newline="") as outputf:
            InvestigationWriter.from_stream(investigation, outputf, quote=args.quotes).write()

    # Write studies and assays
    for s, study_info in enumerate(investigation.studies):
        if output_investigation_file.name == "<stdout>":
            if study_info.info.path:
                StudyWriter.from_stream(
                    studies[s], output_investigation_file, quote=args.quotes
                ).write()
            for a, assay_info in enumerate(study_info.assays):
                if assay_info.path:
                    AssayWriter.from_stream(
                        assays[s][a], output_investigation_file, quote=args.quotes
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


@app.command()
def main(
    input_investigation_file: Annotated[
        str,
        typer.Option(
            "--input-investigation-file",
            "-i",
            help="Path to input investigation file",
        ),
    ],
    output_investigation_file: Annotated[
        str,
        typer.Option(
            "--output-investigation-file",
            "-o",
            help=(
                'Path to output investigation file, stdout ("-") by default. '
                "Needs to be in a different directory!"
            ),
        ),
    ],
    quotes: Annotated[
        Optional[str],
        typer.Option(
            "--quotes",
            "-q",
            help='Character for quoting, e.g. "\\"" (None by default)',
        ),
    ] = None,
    warnings: Annotated[
        bool,
        typer.Option(
            "--warnings/--no-warnings",
            help="Show ISA-tab related warnings (default is to show)",
        ),
    ] = True,
):
    # Convert to `Arguments` object.
    args = Arguments(
        input_investigation_file=input_investigation_file,
        output_investigation_file=output_investigation_file,
        quotes=quotes,
        warnings=warnings,
    )
    # Start application
    return run(args)


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)

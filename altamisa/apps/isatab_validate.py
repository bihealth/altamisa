# -*- coding: utf-8 -*-
"""Read from ISA-Tab and print validation warnings, if any.
"""

import os
import warnings

import attrs
import typer
from typing_extensions import Annotated

from altamisa.isatab import (
    AssayReader,
    AssayValidator,
    InvestigationReader,
    InvestigationValidator,
    StudyReader,
    StudyValidator,
)

#: Typer application instance.
app = typer.Typer()


@attrs.define
class Arguments:
    input_investigation_file: str
    show_duplicate_warnings: bool


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
    show_duplicate_warnings: Annotated[
        bool,
        typer.Option(
            "--show-duplicate-warnings/--no-show-duplicate_warnings",
            help="Show duplicated warnings, i.e. with same message and same category (False by default)",
        ),
    ] = False,
):
    """Main entry point."""
    # Convert to `Arguments` object.
    args = Arguments(
        input_investigation_file=input_investigation_file,
        show_duplicate_warnings=show_duplicate_warnings,
    )
    # Show all warnings of same type and content
    if args.show_duplicate_warnings:
        warnings.simplefilter("always")

    # Collect warnings
    with warnings.catch_warnings(record=True) as records:
        run_warnings_caught(args)

    # Print warnings
    for record in records:
        warnings.showwarning(
            record.message, record.category, record.filename, lineno=record.lineno, line=record.line
        )


def run_warnings_caught(args: Arguments):
    # Read investigation
    with open(args.input_investigation_file, "rt") as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()

    # Validate investigation
    InvestigationValidator(investigation).validate()

    # Read studies and assays
    path_in = os.path.normpath(os.path.dirname(args.input_investigation_file))
    studies = {}
    assays = {}
    for s, study_info in enumerate(investigation.studies):
        if study_info.info.path:
            with open(os.path.join(path_in, study_info.info.path), "rt") as inputf:
                studies[s] = StudyReader.from_stream(f"S{s + 1}", inputf).read()
        if study_info.assays:
            assays[s] = {}
        for a, assay_info in enumerate(study_info.assays):
            if assay_info.path:
                with open(os.path.join(path_in, assay_info.path), "rt") as inputf:
                    assays[s][a] = AssayReader.from_stream(f"S{s + 1}", f"A{a + 1}", inputf).read()

    # Validate studies and assays
    for s, study_info in enumerate(investigation.studies):
        if study_info.info.path:
            StudyValidator(investigation, study_info, studies[s]).validate()
        for a, assay_info in enumerate(study_info.assays):
            if assay_info.path:
                AssayValidator(
                    investigation, study_info, assay_info, assays[s][a], studies[s]
                ).validate()


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)

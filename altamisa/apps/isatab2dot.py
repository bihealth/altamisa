# -*- coding: utf-8 -*-
"""Conversion of ISA-Tab to dot.
"""

from contextlib import ExitStack
import json
import os
import sys

import attrs
import typer
from typing_extensions import Annotated

from altamisa.isatab import AssayReader, InvestigationReader, StudyReader

#: Typer application instance.
app = typer.Typer()


@attrs.define
class Arguments:
    investigation_file: str
    output_file: str


def print_dot(
    obj,
    outf,
    indent="    ",
    mat_shape="box",
    mat_color="black",
    proc_shape="ellipse",
    proc_color="blue",
):
    print(indent + "/* materials */", file=outf)
    for name, mat in obj.materials.items():
        label = json.dumps(f"{mat.type}:\n{mat.name if mat.name else '-'}\n({name})")
        print(
            f"{indent}{json.dumps(name)} [label={label},shape={mat_shape},color={mat_color},fontcolor={mat_color}]",
            file=outf,
        )
    print(indent + "/* processes */", file=outf)
    for name, proc in obj.processes.items():
        label = json.dumps(
            "Process:\n{}\n{}\n({})".format(
                proc.protocol_ref if proc.protocol_ref else "-",
                proc.name if proc.name else "-",
                name,
            )
        )
        print(
            "{}{} [label={},shape={},color={},fontcolor={}]".format(
                indent, json.dumps(name), label, proc_shape, proc_color, proc_color
            ),
            file=outf,
        )
    print(indent + "/* arcs */", file=outf)
    for arc in obj.arcs:
        print(f"{indent}{json.dumps(arc.tail)} -> {json.dumps(arc.head)};", file=outf)


def run(args: Arguments):
    with open(args.investigation_file, "rt") as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()

    path = os.path.dirname(args.investigation_file)

    with ExitStack() as stack:
        if args.output_file == "-":
            output_file = sys.stdout
        else:
            output_file = stack.enter_context(open(args.output_file, "wt"))

        print("digraph investigation {", file=output_file)
        print('  rankdir = "LR";', file=output_file)

        for s, study_info in enumerate(investigation.studies):
            if not study_info.info.path:
                print(f"  /* no file for study {s + 1} */", file=output_file)
                continue
            with open(os.path.join(path, study_info.info.path), "rt") as inputf:
                study = StudyReader.from_stream(f"S{s + 1}", inputf).read()
            print(f"  /* study {study_info.info.path} */", file=output_file)
            print(f"  subgraph clusterStudy{s} {{", file=output_file)
            print(f'    label = "Study: {study_info.info.path}"', file=output_file)
            print_dot(study, output_file)
            print("  }", file=output_file)

            for a, assay_info in enumerate(study_info.assays):
                if not assay_info.path:
                    print(f"  /* no file for assay {a + 1} */", file=output_file)
                    continue
                with open(os.path.join(path, assay_info.path), "rt") as inputf:
                    assay = AssayReader.from_stream(f"S{s + 1}", f"A{a + 1}", inputf).read()
                print(f"  /* assay {assay_info.path} */", file=output_file)
                print(f"  subgraph clusterAssayS{s}A{a} {{", file=output_file)
                print(f'    label = "Assay: {assay_info.path}"', file=output_file)
                print_dot(assay, output_file)
                print("  }", file=output_file)

        print("}", file=output_file)


@app.command()
def main(
    investigation_file: Annotated[
        str,
        typer.Option(
            "--investigation-file",
            "-i",
            help="Path to input investigation file",
        ),
    ],
    output_file: Annotated[
        str,
        typer.Option(
            "--output-file",
            "-o",
            help="Path to output file, stdout ('-') by default",
        ),
    ] = "-",
):
    """Main entry point."""
    # Convert to `Arguments` object.
    args = Arguments(
        investigation_file=investigation_file,
        output_file=output_file,
    )
    # Actually run.
    run(args)


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)

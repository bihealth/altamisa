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
        label = json.dumps("{}:\n{}\n({})".format(mat.type, mat.name if mat.name else "-", name))
        print(
            "{}{} [label={},shape={},color={},fontcolor={}]".format(
                indent, json.dumps(name), label, mat_shape, mat_color, mat_color
            ),
            file=outf,
        )
    print(indent + "/* processes */", file=outf)
    for name, proc in obj.processes.items():
        label = json.dumps(
            "{}:\n{}\n{}\n({})".format(
                "Process",
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
        print("{}{} -> {};".format(indent, json.dumps(arc.tail), json.dumps(arc.head)), file=outf)


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
                print("  /* no file for study {} */".format(s + 1), file=output_file)
                continue
            with open(os.path.join(path, study_info.info.path), "rt") as inputf:
                study = StudyReader.from_stream("S{}".format(s + 1), inputf).read()
            print("  /* study {} */".format(study_info.info.path), file=output_file)
            print("  subgraph clusterStudy{} {{".format(s), file=output_file)
            print('    label = "Study: {}"'.format(study_info.info.path), file=output_file)
            print_dot(study, output_file)
            print("  }", file=output_file)

            for a, assay_info in enumerate(study_info.assays):
                if not assay_info.path:
                    print("  /* no file for assay {} */".format(a + 1), file=output_file)
                    continue
                with open(os.path.join(path, assay_info.path), "rt") as inputf:
                    assay = AssayReader.from_stream(
                        "S{}".format(s + 1), "A{}".format(a + 1), inputf
                    ).read()
                print("  /* assay {} */".format(assay_info.path), file=output_file)
                print("  subgraph clusterAssayS{}A{} {{".format(s, a), file=output_file)
                print('    label = "Assay: {}"'.format(assay_info.path), file=output_file)
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

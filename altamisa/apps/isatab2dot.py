# -*- coding: utf-8 -*-
"""Conversion of ISA-Tab to dot.
"""

import json
import sys
import os
import argparse

from altamisa.isatab import InvestigationReader, StudyReader, AssayReader


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


def run(args):
    with open(args.investigation_file, "rt") as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()

    path = os.path.dirname(args.investigation_file)

    print("digraph investigation {", file=args.output_file)
    print('  rankdir = "LR";', file=args.output_file)

    for s, study_info in enumerate(investigation.studies):
        with open(os.path.join(path, study_info.info.path), "rt") as inputf:
            study = StudyReader.from_stream("S{}".format(s + 1), inputf).read()
        print("  /* study {} */".format(study_info.info.path), file=args.output_file)
        print("  subgraph clusterStudy{} {{".format(s), file=args.output_file)
        print('    label = "Study: {}"'.format(study_info.info.path), file=args.output_file)
        print_dot(study, args.output_file)
        print("  }", file=args.output_file)

        for a, assay_info in enumerate(study_info.assays):
            with open(os.path.join(path, assay_info.path), "rt") as inputf:
                assay = AssayReader.from_stream(
                    "S{}".format(s + 1), "A{}".format(a + 1), inputf
                ).read()
            print("  /* assay {} */".format(assay_info.path), file=args.output_file)
            print("  subgraph clusterAssayS{}A{} {{".format(s, a), file=args.output_file)
            print('    label = "Assay: {}"'.format(assay_info.path), file=args.output_file)
            print_dot(assay, args.output_file)
            print("  }", file=args.output_file)

    print("}", file=args.output_file)


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--investigation-file", required=True, help="Path to investigation file"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default="-",
        type=argparse.FileType("wt"),
        help='Path to output file, stdout ("-") by default',
    )

    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

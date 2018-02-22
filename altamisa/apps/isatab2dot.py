# -*- coding: utf-8 -*-
"""Conversion of ISA-Tab to dot.
"""

import json
import sys
import argparse

from altamisa.isatab import InvestigationReader, StudyReader, AssayReader


def print_dot(
        obj, outf, indent='    ',
        mat_shape='box', mat_color='black',
        proc_shape='ellipse', proc_color='blue'):
    print(indent + '/* materials */', file=outf)
    for name, _ in obj.materials.items():
        print('{}{} [shape={},color={},fontcolor={}]'.format(
            indent, json.dumps(name), mat_shape, mat_color,
            mat_color
        ), file=outf)
    print(indent + '/* processes */', file=outf)
    for name, _ in obj.processes.items():
        print('{}{} [shape={},color={},fontcolor={}]'.format(
            indent, json.dumps(name), proc_shape, proc_color,
            proc_color
        ), file=outf)
    print(indent + '/* arcs */', file=outf)
    for arc in obj.arcs:
        print('{}{} -> {};'.format(
            indent,
            json.dumps(arc.tail),
            json.dumps(arc.head),
        ), file=outf)


def run(args):
    with open(args.investigation_file, 'rt') as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()
    with open(args.study_file, 'rt') as inputf:
        study = StudyReader.from_stream(investigation, inputf).read()
    with open(args.assay_file, 'rt') as inputf:
        assay = AssayReader.from_stream(investigation, inputf).read()

    print('digraph investigation {', file=args.output_file)
    print('  rankdir = "LR";', file=args.output_file)
    print('  /* study */', file=args.output_file)
    print_dot(study, args.output_file)
    print('  /* assay */', file=args.output_file)
    print_dot(assay, args.output_file)
    print('}', file=args.output_file)


def main(argv=None):
    parser = argparse.ArgumentParser()

    # TODO: reading investigation file is enough after it is properly parsed
    parser.add_argument(
        '-i', '--investigation-file', required=True,
        help='Path to investigation file')
    parser.add_argument(
        '-s', '--study-file', required=True,
        help='Path to study file')
    parser.add_argument(
        '-a', '--assay-file', required=True,
        help='Path to assay file')
    parser.add_argument(
        '-o', '--output-file', default="-", type=argparse.FileType('wt'),
        help='Path to output file, stdout ("-") by default')

    args = parser.parse_args(argv)
    return run(args)


if __name__ == '__main__':
    sys.exit(main())

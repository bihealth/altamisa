# -*- coding: utf-8 -*-
"""Conversion of ISA-Tab to dot.
"""

import json
import sys
import os
import argparse

from altamisa.isatab import InvestigationReader, StudyReader, AssayReader


def print_dot(
        obj, outf, studyid, assayid='', indent='    ',
        mat_shape='box', mat_color='black',
        proc_shape='ellipse', proc_color='blue'):

    print(indent + '/* materials */', file=outf)
    for name, mat in obj.materials.items():
        assayid_mat = assayid if mat.type != "Sample Name" else ''
        print('{}{} [shape={},color={},fontcolor={}]'.format(
            indent, json.dumps('{} ({}{})'.format(name, studyid, assayid_mat)),
            mat_shape, mat_color, mat_color
        ), file=outf)
    print(indent + '/* processes */', file=outf)
    for name, _ in obj.processes.items():
        print('{}{} [shape={},color={},fontcolor={}]'.format(
            indent, json.dumps('{} ({}{})'.format(name, studyid, assayid)),
            proc_shape, proc_color, proc_color
        ), file=outf)
    print(indent + '/* arcs */', file=outf)
    for arc in obj.arcs:
        assayid_tail = assayid
        if (arc.tail in obj.materials
                and obj.materials[arc.tail].type == "Sample Name"):
            assayid_tail = ''
        print('{}{} -> {};'.format(
            indent,
            json.dumps('{} ({}{})'.format(arc.tail, studyid, assayid_tail)),
            json.dumps('{} ({}{})'.format(arc.head, studyid, assayid))
        ), file=outf)


def run(args):
    with open(args.investigation_file, 'rt') as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()

    path = os.path.dirname(args.investigation_file)

    print('digraph investigation {', file=args.output_file)
    print('  rankdir = "LR";', file=args.output_file)

    for s, studyInfo in enumerate(investigation.studies):
        with open(os.path.join(path, studyInfo.info.path), 'rt') as inputf:
            study = StudyReader.from_stream(investigation, inputf).read()
        print('  /* study {} */'.format(studyInfo.info.path),
              file=args.output_file)
        print('  subgraph clusterStudy{} {{'.format(s), file=args.output_file)
        print('    label = "Study: {}"'.format(studyInfo.info.path),
              file=args.output_file)
        print_dot(study, args.output_file, 'S{}'.format(s))
        print('  }', file=args.output_file)

        for a, assayInfo in enumerate(studyInfo.assays.values()):
            with open(os.path.join(path, assayInfo.path), 'rt') as inputf:
                assay = AssayReader.from_stream(investigation, inputf).read()
            print('  /* assay {} */'.format(assayInfo.path),
                  file=args.output_file)
            print('  subgraph clusterAssayS{}A{} {{'.format(s, a),
                  file=args.output_file)
            print('    label = "Assay: {}"'.format(assayInfo.path),
                  file=args.output_file)
            print_dot(assay, args.output_file,
                      'S{}'.format(s), 'A{}'.format(a))
            print('  }', file=args.output_file)

    print('}', file=args.output_file)


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', '--investigation-file', required=True,
        help='Path to investigation file')
    parser.add_argument(
        '-o', '--output-file', default="-", type=argparse.FileType('wt'),
        help='Path to output file, stdout ("-") by default')

    args = parser.parse_args(argv)
    return run(args)


if __name__ == '__main__':
    sys.exit(main())

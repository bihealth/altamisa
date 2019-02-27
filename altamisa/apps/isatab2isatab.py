# -*- coding: utf-8 -*-
"""Read from ISA-Tab and directly write to ISA-Tab.
"""

import sys
import argparse

from altamisa.isatab import InvestigationReader
from altamisa.isatab import InvestigationWriter


def run(args):
    # Read investigation
    with open(args.input_investigation_file, "rt") as inputf:
        investigation = InvestigationReader.from_stream(inputf).read()

    # Write investigation
    InvestigationWriter.from_stream(
        investigation, args.output_investigation_file, args.quotes
    ).write()


def main(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--input-investigation-file", required=True, help="Path to input investigation file"
    )
    parser.add_argument(
        "-o",
        "--output-investigation-file",
        default="-",
        type=argparse.FileType("wt"),
        help='Path to output investigation file, stdout ("-") by default',
    )
    parser.add_argument(
        "-q", "--quotes", default=None, help="Quotes to be used around fields, None by default"
    )

    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())

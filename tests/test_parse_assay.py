# -*- coding: utf-8 -*-
"""Tests for parsing ISA assay files"""


import io
import os
import pytest

from altamisa.constants import table_headers
from altamisa.exceptions import IsaWarning
from altamisa.isatab import models
from altamisa.isatab import (
    InvestigationReader,
    InvestigationValidator,
    AssayRowReader,
    AssayReader,
    AssayValidator,
)


def test_assay_row_reader_minimal_assay(minimal_investigation_file, minimal_assay_file):
    """Use ``AssayRowReader`` to read in minimal assay file."""

    # Create new row reader and check read headers
    row_reader = AssayRowReader.from_stream("S1", "A1", minimal_assay_file)
    assert 5 == len(row_reader.header)

    # Read all rows in assay
    rows = list(row_reader.read())

    # Check results
    assert 1 == len(rows)
    first_row = rows[0]

    assert 4 == len(first_row)

    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == first_row[0]
    expected = models.Process(
        "nucleic acid sequencing",
        "S1-A1-0815-N1-DNA1-WES1-3",
        "0815-N1-DNA1-WES1",
        "Assay Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )
    assert expected == first_row[1]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4",
        "0815-N1-DNA1-WES1_L???_???_R1.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == first_row[2]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5",
        "0815-N1-DNA1-WES1_L???_???_R2.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == first_row[3]


def test_assay_reader_minimal_assay(minimal_investigation_file, minimal_assay_file):
    """Use ``AssayReader`` to read in minimal assay file.

    Using the ``AssayReader`` instead of the ``AssayRowReader`` gives us
    ``Assay`` objects instead of just the row-wise nodes.
    """
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 2 == len(record)

    # Create new row reader and check read headers
    reader = AssayReader.from_stream("S1", "A1", minimal_assay_file)
    assert 5 == len(reader.header)

    # Read and validate assay
    assay = reader.read()
    AssayValidator(
        investigation, investigation.studies[0], investigation.studies[0].assays[0], assay
    ).validate()

    # Check results
    assert os.path.normpath(str(assay.file)).endswith(
        os.path.normpath("data/i_minimal/a_minimal.txt")
    )
    assert 5 == len(assay.header)
    assert 3 == len(assay.materials)
    assert 1 == len(assay.processes)
    assert 3 == len(assay.arcs)

    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == assay.materials["S1-sample-0815-N1"]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4",
        "0815-N1-DNA1-WES1_L???_???_R1.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4"]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5",
        "0815-N1-DNA1-WES1_L???_???_R2.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5"]

    expected = models.Process(
        "nucleic acid sequencing",
        "S1-A1-0815-N1-DNA1-WES1-3",
        "0815-N1-DNA1-WES1",
        "Assay Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )
    assert expected == assay.processes["S1-A1-0815-N1-DNA1-WES1-3"]

    expected = (
        models.Arc("S1-sample-0815-N1", "S1-A1-0815-N1-DNA1-WES1-3"),
        models.Arc(
            "S1-A1-0815-N1-DNA1-WES1-3", "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4"
        ),
        models.Arc(
            "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4",
            "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5",
        ),
    )
    assert expected == assay.arcs


def test_assay_row_reader_small_assay(small_investigation_file, small_assay_file):
    """Use ``AssayRowReader`` to read in small assay file."""

    # Create new row reader and check read headers
    row_reader = AssayRowReader.from_stream("S1", "A1", small_assay_file)
    assert 9 == len(row_reader.header)

    # Read all rows in assay
    rows = list(row_reader.read())

    # Check results
    assert 2 == len(rows)
    first_row = rows[0]
    second_row = rows[1]

    assert 8 == len(first_row)

    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == first_row[0]

    expected = models.Process(
        "library preparation",
        "S1-A1-library preparation-2-1",
        None,
        None,
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF],
    )
    assert expected == first_row[1]

    expected = models.Material(
        "Library Name",
        "S1-A1-0815-N1-DNA1-COL3",
        "0815-N1-DNA1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.LIBRARY_NAME],
    )
    assert expected == first_row[2]

    expected = models.Process(
        "nucleic acid sequencing",
        "S1-A1-0815-N1-DNA1-WES1-5",
        "0815-N1-DNA1-WES1",
        "Assay Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )
    assert expected == first_row[3]

    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL6",
        "0815-N1-DNA1-WES1_L???_???_R1.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == first_row[4]

    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL7",
        "0815-N1-DNA1-WES1_L???_???_R2.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == first_row[5]

    expected = models.Process(
        "Unknown",
        "S1-A1-somatic variant calling-1-8",
        "somatic variant calling-1",
        "Data Transformation Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.DATA_TRANSFORMATION_NAME],
    )
    assert expected == first_row[6]

    expected = models.Material(
        "Derived Data File",
        "S1-A1-0815-somatic.vcf.gz-COL9",
        "0815-somatic.vcf.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.DERIVED_DATA_FILE],
    )
    assert expected == first_row[7]

    assert 8 == len(second_row)

    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-T1",
        "0815-T1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == second_row[0]

    expected = models.Process(
        "library preparation",
        "S1-A1-library preparation-2-2",
        None,
        None,
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF],
    )
    assert expected == second_row[1]

    expected = models.Material(
        "Library Name",
        "S1-A1-0815-T1-DNA1-COL3",
        "0815-T1-DNA1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.LIBRARY_NAME],
    )
    assert expected == second_row[2]

    expected = models.Process(
        "nucleic acid sequencing",
        "S1-A1-0815-T1-DNA1-WES1-5",
        "0815-T1-DNA1-WES1",
        "Assay Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )
    assert expected == second_row[3]

    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL6",
        "0815-T1-DNA1-WES1_L???_???_R1.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == second_row[4]

    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL7",
        "0815-T1-DNA1-WES1_L???_???_R2.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == second_row[5]

    expected = models.Process(
        "Unknown",
        "S1-A1-somatic variant calling-1-8",
        "somatic variant calling-1",
        "Data Transformation Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.DATA_TRANSFORMATION_NAME],
    )
    assert expected == second_row[6]

    expected = models.Material(
        "Derived Data File",
        "S1-A1-0815-somatic.vcf.gz-COL9",
        "0815-somatic.vcf.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.DERIVED_DATA_FILE],
    )
    assert expected == second_row[7]


def test_assay_reader_small_assay(small_investigation_file, small_assay_file):
    """Use ``AssayReader`` to read in small assay file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 2 == len(record)

    # Create new row reader and check read headers
    reader = AssayReader.from_stream("S1", "A1", small_assay_file)
    assert 9 == len(reader.header)

    # Read assay
    with pytest.warns(IsaWarning) as record:
        assay = reader.read()
        AssayValidator(
            investigation, investigation.studies[0], investigation.studies[0].assays[0], assay
        ).validate()

    # Check warnings
    assert 1 == len(record)

    # Check results
    assert os.path.normpath(str(assay.file)).endswith(os.path.normpath("data/i_small/a_small.txt"))
    assert 9 == len(assay.header)
    assert 9 == len(assay.materials)
    assert 5 == len(assay.processes)
    assert 13 == len(assay.arcs)

    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == assay.materials["S1-sample-0815-N1"]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-T1",
        "0815-T1",
        None,
        (),
        (),
        (),
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == assay.materials["S1-sample-0815-T1"]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL6",
        "0815-N1-DNA1-WES1_L???_???_R1.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL6"]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL7",
        "0815-N1-DNA1-WES1_L???_???_R2.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL7"]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL6",
        "0815-T1-DNA1-WES1_L???_???_R1.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL6"]
    expected = models.Material(
        "Raw Data File",
        "S1-A1-0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL7",
        "0815-T1-DNA1-WES1_L???_???_R2.fastq.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.RAW_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL7"]
    expected = models.Material(
        "Derived Data File",
        "S1-A1-0815-somatic.vcf.gz-COL9",
        "0815-somatic.vcf.gz",
        None,
        (),
        (),
        (),
        None,
        [table_headers.DERIVED_DATA_FILE],
    )
    assert expected == assay.materials["S1-A1-0815-somatic.vcf.gz-COL9"]

    expected = models.Process(
        "library preparation",
        "S1-A1-library preparation-2-1",
        None,
        None,
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF],
    )
    assert expected == assay.processes["S1-A1-library preparation-2-1"]
    expected = models.Process(
        "library preparation",
        "S1-A1-library preparation-2-2",
        None,
        None,
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF],
    )
    assert expected == assay.processes["S1-A1-library preparation-2-2"]
    expected = models.Process(
        "nucleic acid sequencing",
        "S1-A1-0815-N1-DNA1-WES1-5",
        "0815-N1-DNA1-WES1",
        "Assay Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )
    assert expected == assay.processes["S1-A1-0815-N1-DNA1-WES1-5"]
    expected = models.Process(
        "nucleic acid sequencing",
        "S1-A1-0815-T1-DNA1-WES1-5",
        "0815-T1-DNA1-WES1",
        "Assay Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )
    assert expected == assay.processes["S1-A1-0815-T1-DNA1-WES1-5"]

    expected = (
        models.Arc("S1-sample-0815-N1", "S1-A1-library preparation-2-1"),
        models.Arc("S1-A1-library preparation-2-1", "S1-A1-0815-N1-DNA1-COL3"),
        models.Arc("S1-A1-0815-N1-DNA1-COL3", "S1-A1-0815-N1-DNA1-WES1-5"),
        models.Arc(
            "S1-A1-0815-N1-DNA1-WES1-5", "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL6"
        ),
        models.Arc(
            "S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL6",
            "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL7",
        ),
        models.Arc(
            "S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL7", "S1-A1-somatic variant calling-1-8"
        ),
        models.Arc("S1-A1-somatic variant calling-1-8", "S1-A1-0815-somatic.vcf.gz-COL9"),
        models.Arc("S1-sample-0815-T1", "S1-A1-library preparation-2-2"),
        models.Arc("S1-A1-library preparation-2-2", "S1-A1-0815-T1-DNA1-COL3"),
        models.Arc("S1-A1-0815-T1-DNA1-COL3", "S1-A1-0815-T1-DNA1-WES1-5"),
        models.Arc(
            "S1-A1-0815-T1-DNA1-WES1-5", "S1-A1-0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL6"
        ),
        models.Arc(
            "S1-A1-0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL6",
            "S1-A1-0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL7",
        ),
        models.Arc(
            "S1-A1-0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL7", "S1-A1-somatic variant calling-1-8"
        ),
    )
    assert expected == assay.arcs


def test_assay_reader_small2_assay(small2_investigation_file, small2_assay_file):
    """Use ``AssayReader`` to read in small assay file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small2_investigation_file).read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 1 == len(record)

    # Create new row reader and check read headers
    reader = AssayReader.from_stream("S1", "A1", small2_assay_file)
    assert 14 == len(reader.header)

    # Read assay
    assay = reader.read()
    AssayValidator(
        investigation, investigation.studies[0], investigation.studies[0].assays[0], assay
    ).validate()

    # Check results
    assert os.path.normpath(str(assay.file)).endswith(
        os.path.normpath("data/i_small2/a_small2.txt")
    )
    assert 14 == len(assay.header)
    assert 25 == len(assay.materials)
    assert 41 == len(assay.processes)
    assert 74 == len(assay.arcs)

    # Comments
    expected = models.Comment(name="Replicate", value="B")
    assert assay.materials["S1-A1-0815-T1-Pro1-B-115-COL5"].comments[0] == expected

    # Expected arcs
    expected = (
        models.Arc("S1-sample-0815-N1", "S1-A1-extraction-2-1"),
        models.Arc("S1-sample-0815-T1", "S1-A1-extraction-2-2"),
        models.Arc("S1-A1-extraction-2-1", "S1-A1-0815-N1-Pro1-COL3"),
        models.Arc("S1-A1-extraction-2-2", "S1-A1-0815-T1-Pro1-COL3"),
        models.Arc("S1-A1-0815-N1-Pro1-COL3", "S1-A1-labeling-4-1"),
        models.Arc("S1-A1-0815-T1-Pro1-COL3", "S1-A1-labeling-4-2"),
        models.Arc("S1-A1-0815-N1-Pro1-COL3", "S1-A1-labeling-4-3"),
        models.Arc("S1-A1-0815-T1-Pro1-COL3", "S1-A1-labeling-4-4"),
        models.Arc("S1-A1-0815-N1-Pro1-COL3", "S1-A1-labeling-4-5"),
        models.Arc("S1-A1-0815-T1-Pro1-COL3", "S1-A1-labeling-4-6"),
        models.Arc("S1-A1-0815-N1-Pro1-COL3", "S1-A1-labeling-4-7"),
        models.Arc("S1-A1-0815-T1-Pro1-COL3", "S1-A1-labeling-4-8"),
        models.Arc("S1-A1-0815-N1-Pro1-COL3", "S1-A1-labeling-4-9"),
        models.Arc("S1-A1-0815-T1-Pro1-COL3", "S1-A1-labeling-4-10"),
        models.Arc("S1-A1-0815-N1-Pro1-COL3", "S1-A1-labeling-4-11"),
        models.Arc("S1-A1-0815-T1-Pro1-COL3", "S1-A1-labeling-4-12"),
        models.Arc("S1-A1-labeling-4-1", "S1-A1-0815-N1-Pro1-A-114-COL5"),
        models.Arc("S1-A1-labeling-4-2", "S1-A1-0815-T1-Pro1-A-115-COL5"),
        models.Arc("S1-A1-labeling-4-3", "S1-A1-0815-N1-Pro1-B-114-COL5"),
        models.Arc("S1-A1-labeling-4-4", "S1-A1-0815-T1-Pro1-B-115-COL5"),
        models.Arc("S1-A1-labeling-4-5", "S1-A1-0815-N1-Pro1-C-114-COL5"),
        models.Arc("S1-A1-labeling-4-6", "S1-A1-0815-T1-Pro1-C-115-COL5"),
        models.Arc("S1-A1-labeling-4-7", "S1-A1-0815-N1-Pro1-D-114-COL5"),
        models.Arc("S1-A1-labeling-4-8", "S1-A1-0815-T1-Pro1-D-115-COL5"),
        models.Arc("S1-A1-labeling-4-9", "S1-A1-0815-N1-Pro1-E-114-COL5"),
        models.Arc("S1-A1-labeling-4-10", "S1-A1-0815-T1-Pro1-E-115-COL5"),
        models.Arc("S1-A1-labeling-4-11", "S1-A1-0815-N1-Pro1-F-114-COL5"),
        models.Arc("S1-A1-labeling-4-12", "S1-A1-0815-T1-Pro1-F-115-COL5"),
        models.Arc("S1-A1-0815-N1-Pro1-A-114-COL5", "S1-A1-chromatography-8-1"),
        models.Arc("S1-A1-0815-T1-Pro1-A-115-COL5", "S1-A1-chromatography-8-2"),
        models.Arc("S1-A1-0815-N1-Pro1-B-114-COL5", "S1-A1-chromatography-8-3"),
        models.Arc("S1-A1-0815-T1-Pro1-B-115-COL5", "S1-A1-chromatography-8-4"),
        models.Arc("S1-A1-0815-N1-Pro1-C-114-COL5", "S1-A1-chromatography-8-5"),
        models.Arc("S1-A1-0815-T1-Pro1-C-115-COL5", "S1-A1-chromatography-8-6"),
        models.Arc("S1-A1-0815-N1-Pro1-D-114-COL5", "S1-A1-chromatography-8-7"),
        models.Arc("S1-A1-0815-T1-Pro1-D-115-COL5", "S1-A1-chromatography-8-8"),
        models.Arc("S1-A1-0815-N1-Pro1-E-114-COL5", "S1-A1-chromatography-8-9"),
        models.Arc("S1-A1-0815-T1-Pro1-E-115-COL5", "S1-A1-chromatography-8-10"),
        models.Arc("S1-A1-0815-N1-Pro1-F-114-COL5", "S1-A1-chromatography-8-11"),
        models.Arc("S1-A1-0815-T1-Pro1-F-115-COL5", "S1-A1-chromatography-8-12"),
        models.Arc("S1-A1-chromatography-8-1", "S1-A1-poolA-10"),
        models.Arc("S1-A1-chromatography-8-2", "S1-A1-poolA-10"),
        models.Arc("S1-A1-chromatography-8-3", "S1-A1-mass spectrometry-9-3"),
        models.Arc("S1-A1-chromatography-8-4", "S1-A1-mass spectrometry-9-4"),
        models.Arc("S1-A1-chromatography-8-5", "S1-A1-poolC-10"),
        models.Arc("S1-A1-chromatography-8-6", "S1-A1-poolC-10"),
        models.Arc("S1-A1-chromatography-8-7", "S1-A1-mass spectrometry-9-7"),
        models.Arc("S1-A1-chromatography-8-8", "S1-A1-mass spectrometry-9-8"),
        models.Arc("S1-A1-chromatography-8-9", "S1-A1-poolE-10"),
        models.Arc("S1-A1-chromatography-8-10", "S1-A1-poolE-10"),
        models.Arc("S1-A1-chromatography-8-11", "S1-A1-poolF-10"),
        models.Arc("S1-A1-chromatography-8-12", "S1-A1-poolF-10"),
        models.Arc("S1-A1-poolA-10", "S1-A1-poolA.raw-COL11"),
        models.Arc("S1-A1-mass spectrometry-9-3", "S1-A1-poolB.raw-COL11"),
        models.Arc("S1-A1-mass spectrometry-9-4", "S1-A1-poolB.raw-COL11"),
        models.Arc("S1-A1-poolC-10", "S1-A1-Empty Raw Spectral Data File-11-5"),
        models.Arc("S1-A1-mass spectrometry-9-7", "S1-A1-Empty Raw Spectral Data File-11-7"),
        models.Arc("S1-A1-mass spectrometry-9-8", "S1-A1-Empty Raw Spectral Data File-11-8"),
        models.Arc("S1-A1-poolE-10", "S1-A1-poolE.raw-COL11"),
        models.Arc("S1-A1-poolF-10", "S1-A1-Empty Raw Spectral Data File-11-11"),
        models.Arc("S1-A1-poolA.raw-COL11", "S1-A1-data transformation-12-1"),
        models.Arc("S1-A1-poolB.raw-COL11", "S1-A1-data transformation-12-3"),
        models.Arc("S1-A1-Empty Raw Spectral Data File-11-5", "S1-A1-data transformation-12-5"),
        models.Arc("S1-A1-Empty Raw Spectral Data File-11-7", "S1-A1-data transformation-12-7"),
        models.Arc("S1-A1-Empty Raw Spectral Data File-11-8", "S1-A1-data transformation-12-8"),
        models.Arc("S1-A1-poolE.raw-COL11", "S1-A1-data transformation-12-9"),
        models.Arc("S1-A1-Empty Raw Spectral Data File-11-11", "S1-A1-data analysis-13"),
        models.Arc("S1-A1-data transformation-12-1", "S1-A1-results.csv-COL14"),
        models.Arc("S1-A1-data transformation-12-3", "S1-A1-results.csv-COL14"),
        models.Arc("S1-A1-data transformation-12-5", "S1-A1-results.csv-COL14"),
        models.Arc("S1-A1-data transformation-12-7", "S1-A1-results.csv-COL14"),
        models.Arc("S1-A1-data transformation-12-8", "S1-A1-results.csv-COL14"),
        models.Arc("S1-A1-data transformation-12-9", "S1-A1-Empty Derived Data File-14-9"),
        models.Arc("S1-A1-data analysis-13", "S1-A1-results.csv-COL14"),
    )
    assert sorted(expected) == sorted(assay.arcs)


def test_assay_reader_gelelect(gelelect_investigation_file, gelelect_assay_file):
    """Use ``AssayReader`` to read in small assay file."""
    with pytest.warns(IsaWarning) as record:
        # Load investigation
        investigation = InvestigationReader.from_stream(gelelect_investigation_file).read()
        InvestigationValidator(investigation).validate()

        # Create new row reader and check read headers
        reader = AssayReader.from_stream("S1", "A1", gelelect_assay_file)
        assert 22 == len(reader.header)

        # Read assay
        assay = reader.read()
        AssayValidator(
            investigation, investigation.studies[0], investigation.studies[0].assays[0], assay
        ).validate()

    # Check warnings
    assert 5 == len(record)

    # Check results
    assert os.path.normpath(str(assay.file)).endswith(
        os.path.normpath(
            "data/test_gelelect/a_study01_protein_expression_profiling_gel_electrophoresis.txt"
        )
    )
    assert 22 == len(assay.header)
    assert 10 == len(assay.materials)
    assert 11 == len(assay.processes)
    assert 20 == len(assay.arcs)

    expected = models.Material(
        "Image File",
        "S1-A1-Image01.jpeg-COL19",
        "Image01.jpeg",
        None,
        (),
        (),
        (),
        None,
        [table_headers.IMAGE_FILE],
    )
    assert expected == assay.materials["S1-A1-Image01.jpeg-COL19"]

    expected = models.Process(
        "data collection",
        "S1-A1-Scan02-18",
        "Scan02",
        "Scan Name",
        None,
        None,
        (),
        (),
        None,
        None,
        None,
        [table_headers.PROTOCOL_REF, table_headers.SCAN_NAME],
    )
    assert expected == assay.processes["S1-A1-Scan02-18"]

    header_electrophoresis = [
        table_headers.PROTOCOL_REF,
        table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME,
        table_headers.FIRST_DIMENSION,
        table_headers.TERM_SOURCE_REF,
        table_headers.TERM_ACCESSION_NUMBER,
        table_headers.SECOND_DIMENSION,
        table_headers.TERM_SOURCE_REF,
        table_headers.TERM_ACCESSION_NUMBER,
    ]

    expected = models.Process(
        "electrophoresis",
        "S1-A1-Assay01-10",
        "Assay01",
        "Gel Electrophoresis Assay Name",
        None,
        None,
        (),
        (),
        None,
        models.OntologyTermRef("", "", ""),
        models.OntologyTermRef("", "", ""),
        header_electrophoresis,
    )
    assert expected == assay.processes["S1-A1-Assay01-10"]

    expected = models.Process(
        "electrophoresis",
        "S1-A1-electrophoresis-9-2",
        "",
        "Gel Electrophoresis Assay Name",
        None,
        None,
        (),
        (),
        None,
        models.OntologyTermRef("AssayX", None, None),
        models.OntologyTermRef("AssayY", None, None),
        header_electrophoresis,
    )
    assert expected == assay.processes["S1-A1-electrophoresis-9-2"]


def test_assay_reader_minimal_assay_iostring(minimal_investigation_file, minimal_assay_file):
    # Load investigation (tested elsewhere)
    stringio = io.StringIO(minimal_investigation_file.read())
    investigation = InvestigationReader.from_stream(stringio).read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 2 == len(record)

    stringio = io.StringIO(minimal_assay_file.read())

    # Create new assay reader and read from StringIO with original filename indicated
    reader = AssayReader.from_stream("S1", "A1", stringio, filename="data/i_minimal/a_minimal.txt")
    assert 5 == len(reader.header)

    # Read and validate assay
    assay = reader.read()
    AssayValidator(
        investigation, investigation.studies[0], investigation.studies[0].assays[0], assay
    ).validate()

    # Check results
    assert os.path.normpath(str(assay.file)).endswith(
        os.path.normpath("data/i_minimal/a_minimal.txt")
    )
    assert 5 == len(assay.header)
    assert 3 == len(assay.materials)
    assert 1 == len(assay.processes)
    assert 3 == len(assay.arcs)


def test_assay_reader_minimal_assay_iostring2(minimal_investigation_file, minimal_assay_file):
    # Load investigation (tested elsewhere)
    stringio = io.StringIO(minimal_investigation_file.read())
    investigation = InvestigationReader.from_stream(stringio).read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 2 == len(record)

    # Create new assay reader and read from StringIO with no filename indicated
    stringio = io.StringIO(minimal_assay_file.read())
    reader = AssayReader.from_stream("S1", "A1", stringio)
    assert 5 == len(reader.header)

    # Read and validate assay
    assay = reader.read()
    AssayValidator(
        investigation, investigation.studies[0], investigation.studies[0].assays[0], assay
    ).validate()

    # Check results
    assert str(assay.file) == os.path.normpath("<no file>")
    assert 5 == len(assay.header)
    assert 3 == len(assay.materials)
    assert 1 == len(assay.processes)
    assert 3 == len(assay.arcs)

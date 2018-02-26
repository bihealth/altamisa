# -*- coding: utf-8 -*-
"""Tests for parsing ISA assay files"""

# TODO: test with one annotation for each source, extraction, sample
# TODO: test with secondary annotation (i.e., further qualify with term) or even tertiary (qualify with unit and qualify unit with term)

from datetime import date

import pytest

from altamisa.isatab import models
from altamisa.isatab import InvestigationReader, AssayRowReader, AssayReader


def test_assay_row_reader_minimal_assay(
        minimal_investigation_file, minimal_assay_file):
    """Use ``AssayRowReader`` to read in minimal assay file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = AssayRowReader.from_stream(investigation, minimal_assay_file)
    assert 5 == len(row_reader.header)

    # Read all rows in assay
    rows = list(row_reader.read())

    # Check results
    assert 1 == len(rows)
    first_row = rows[0]

    assert 4 == len(first_row)

    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == first_row[0]
    expected = models.Process(
        'nucleic acid sequencing', '0815-N1-DNA1-WES1', None,
        None, (), (), None, None)
    assert expected == first_row[1]
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4',
        None, (), (), (), None)
    assert expected == first_row[2]
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5',
        None, (), (), (), None)
    assert expected == first_row[3]


def test_assay_reader_minimal_assay(
        minimal_investigation_file, minimal_assay_file):
    """Use ``AssayReader`` to read in minimal assay file.

    Using the ``AssayReader`` instead of the ``AssayRowReader`` gives us
    ``Assay`` objects instead of just the row-wise nodes.
    """
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()

    # Create new row reader and check read headers
    reader = AssayReader.from_stream(investigation, minimal_assay_file)
    assert 5 == len(reader.header)

    # Read assay
    assay = reader.read()

    # Check results
    assert str(assay.file).endswith('data/i_minimal/a_minimal.txt')
    assert 5 == len(assay.header)
    assert 3 == len(assay.materials)
    assert 1 == len(assay.processes)
    assert 3 == len(assay.arcs)

    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == assay.materials['sample-0815-N1']
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4',
        None, (), (), (), None)
    assert expected == assay.materials[
        '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4']
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5',
        None, (), (), (), None)
    assert expected == assay.materials[
        '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5']

    expected = models.Process(
        'nucleic acid sequencing', '0815-N1-DNA1-WES1', None,
        None, (), (), None, None)
    assert expected == assay.processes['0815-N1-DNA1-WES1']

    expected = (
        models.Arc('sample-0815-N1', '0815-N1-DNA1-WES1'),
        models.Arc('0815-N1-DNA1-WES1', '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4'),
        models.Arc('0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4',
                   '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5'),
    )
    assert expected == assay.arcs


def test_assay_row_reader_small_assay(
        small_investigation_file, small_assay_file):
    """Use ``AssayRowReader`` to read in small assay file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = AssayRowReader.from_stream(investigation, small_assay_file)
    assert 8 == len(row_reader.header)

    # Read all rows in assay
    rows = list(row_reader.read())

    # Check results
    assert 2 == len(rows)
    first_row = rows[0]
    second_row = rows[1]

    assert 7 == len(first_row)

    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == first_row[0]
    expected = models.Process(
        'library preparation', 'library preparation-2-1', None,
        None, (), (), None, None)
    assert expected == first_row[1]
    expected = models.Process(
        'nucleic acid sequencing', '0815-N1-DNA1-WES1', None,
        None, (), (), None, None)
    assert expected == first_row[2]
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL5',
        None, (), (), (), None)
    assert expected == first_row[3]
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL6',
        None, (), (), (), None)
    assert expected == first_row[4]
    expected = models.Process(
        'UNKNOWN', 'somatic variant calling-1', None,
        None, (), (), None, None)
    assert expected == first_row[5]
    expected = models.Material(
        'Derived Data File', '0815-somatic.vcf.gz-COL8',
        None, (), (), (), None)
    assert expected == first_row[6]

    assert 7 == len(second_row)

    expected = models.Material(
        'Sample Name', 'sample-0815-T1', None, (), (), (), None)
    assert expected == second_row[0]
    expected = models.Process(
        'library preparation', 'library preparation-2-2', None,
        None, (), (), None, None)
    assert expected == second_row[1]
    expected = models.Process(
        'nucleic acid sequencing', '0815-T1-DNA1-WES1', None,
        None, (), (), None, None)
    assert expected == second_row[2]
    expected = models.Material(
        'Raw Data File', '0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL5',
        None, (), (), (), None)
    assert expected == second_row[3]
    expected = models.Material(
        'Raw Data File', '0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL6',
        None, (), (), (), None)
    assert expected == second_row[4]
    expected = models.Process(
        'UNKNOWN', 'somatic variant calling-1', None,
        None, (), (), None, None)
    assert expected == second_row[5]
    expected = models.Material(
        'Derived Data File', '0815-somatic.vcf.gz-COL8',
        None, (), (), (), None)
    assert expected == second_row[6]


def test_assay_reader_small_assay(
        small_investigation_file, small_assay_file):
    """Use ``AssayReader`` to read in small assay file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    reader = AssayReader.from_stream(investigation, small_assay_file)
    assert 8 == len(reader.header)

    # Read assay
    assay = reader.read()

    # Check results
    assert str(assay.file).endswith('data/i_small/a_small.txt')
    assert 8 == len(assay.header)
    assert 7 == len(assay.materials)
    assert 5 == len(assay.processes)
    assert 11 == len(assay.arcs)

    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == assay.materials['sample-0815-N1']
    expected = models.Material(
        'Sample Name', 'sample-0815-T1', None, (), (), (), None)
    assert expected == assay.materials['sample-0815-T1']
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL5',
        None, (), (), (), None)
    assert expected == assay.materials[
        '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL5']
    expected = models.Material(
        'Raw Data File', '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL6',
        None, (), (), (), None)
    assert expected == assay.materials[
        '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL6']
    expected = models.Material(
        'Raw Data File', '0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL5',
        None, (), (), (), None)
    assert expected == assay.materials[
        '0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL5']
    expected = models.Material(
        'Raw Data File', '0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL6',
        None, (), (), (), None)
    assert expected == assay.materials[
        '0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL6']
    expected = models.Material(
        'Derived Data File', '0815-somatic.vcf.gz-COL8',
        None, (), (), (), None)
    assert expected == assay.materials['0815-somatic.vcf.gz-COL8']

    expected = models.Process(
        'library preparation', 'library preparation-2-1', None,
        None, (), (), None, None)
    assert expected == assay.processes['library preparation-2-1']
    expected = models.Process(
        'library preparation', 'library preparation-2-2', None,
        None, (), (), None, None)
    assert expected == assay.processes['library preparation-2-2']
    expected = models.Process(
        'nucleic acid sequencing', '0815-N1-DNA1-WES1', None,
        None, (), (), None, None)
    assert expected == assay.processes['0815-N1-DNA1-WES1']
    expected = models.Process(
        'nucleic acid sequencing', '0815-T1-DNA1-WES1', None,
        None, (), (), None, None)
    assert expected == assay.processes['0815-T1-DNA1-WES1']

    expected = (
        models.Arc('sample-0815-N1', 'library preparation-2-1'),
        models.Arc('library preparation-2-1', '0815-N1-DNA1-WES1'),
        models.Arc('0815-N1-DNA1-WES1',
                   '0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL5'),
        models.Arc('0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL5',
                   '0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL6'),
        models.Arc('0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL6',
                   'somatic variant calling-1'),
        models.Arc('somatic variant calling-1', '0815-somatic.vcf.gz-COL8'),
        models.Arc('sample-0815-T1', 'library preparation-2-2'),
        models.Arc('library preparation-2-2', '0815-T1-DNA1-WES1'),
        models.Arc('0815-T1-DNA1-WES1',
                   '0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL5'),
        models.Arc('0815-T1-DNA1-WES1_L???_???_R1.fastq.gz-COL5',
                   '0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL6'),
        models.Arc('0815-T1-DNA1-WES1_L???_???_R2.fastq.gz-COL6',
                   'somatic variant calling-1')
    )
    assert expected == assay.arcs
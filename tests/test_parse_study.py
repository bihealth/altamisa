# -*- coding: utf-8 -*-
"""Tests for parsing ISA study files"""

# TODO: test with one annotation for each source, extraction, sample
# TODO: test with secondary annotation (i.e., further qualify with term) or even tertiary (qualify with unit and qualify unit with term)

from datetime import date

import pytest

from altamisa.isatab import models
from altamisa.isatab import InvestigationReader, StudyRowReader, StudyReader


def test_study_row_reader_minimal_study(
        minimal_investigation_file, minimal_study_file):
    """Use ``StudyRowReader`` to read in minimal study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = StudyRowReader.from_stream(
        investigation, "S1", minimal_study_file)
    assert 3 == len(row_reader.header)

    # Read all rows in study
    rows = list(row_reader.read())

    # Check results
    assert 1 == len(rows)
    first_row = rows[0]

    assert 3 == len(first_row)

    expected = models.Material(
        'Source Name', 'source-0815', None, (), (), (), None)
    assert expected == first_row[0]
    expected = models.Process(
        'sample collection', 'sample collection-2-1', None, None,
        (), (), None, None)
    assert expected == first_row[1]
    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == first_row[2]


def test_study_reader_minimal_study(
        minimal_investigation_file, minimal_study_file):
    """Use ``StudyReader`` to read in minimal study file.

    Using the ``StudyReader`` instead of the ``StudyRowReader`` gives us
    ``Study`` objects instead of just the row-wise nodes.
    """
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()

    # Create new row reader and check read headers
    reader = StudyReader.from_stream(
        investigation, "S1", minimal_study_file)
    assert 3 == len(reader.header)

    # Read study
    study = reader.read()

    # Check results
    assert str(study.file).endswith('data/i_minimal/s_minimal.txt')
    assert 3 == len(study.header)
    assert 2 == len(study.materials)
    assert 1 == len(study.processes)
    assert 2 == len(study.arcs)

    expected = models.Material(
        'Source Name', 'source-0815', None, (), (), (), None)
    assert expected == study.materials['source-0815']
    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == study.materials['sample-0815-N1']

    expected = models.Process(
        'sample collection', 'sample collection-2-1', None, None, (), (), None, None)
    assert expected == study.processes['sample collection-2-1']

    expected = (models.Arc('source-0815', 'sample collection-2-1'),
                models.Arc('sample collection-2-1', 'sample-0815-N1'))
    assert expected == study.arcs


def test_study_row_reader_small_study(
        small_investigation_file, small_study_file):
    """Use ``StudyRowReader`` to read in small study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = StudyRowReader.from_stream(
        investigation, "S1", small_study_file)
    assert 7 == len(row_reader.header)

    # Read all rows in study
    rows = list(row_reader.read())

    # Check results
    assert 4 == len(rows)
    first_row = rows[0]
    second_row = rows[1]

    assert 3 == len(first_row)

    characteristics = models.Characteristics(
        name='organism',
        value=models.OntologyTermRef(
            name='Mus musculus',
            accession='http://purl.bioontology.org/ontology/NCBITAXON/10090',
            ontology_name='NCBITAXON'),
        unit=None)

    expected = models.Material(
        'Source Name', 'source-0815', None, (characteristics,), (), (), None)
    assert expected == first_row[0]
    expected = models.Process(
        'sample collection', 'sample collection-5-1', date(2018, 2, 2),
        'John Doe', (), (), None, None)
    assert expected == first_row[1]
    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == first_row[2]

    assert 3 == len(second_row)
    expected = models.Material(
        'Source Name', 'source-0815', None, (characteristics,), (), (), None)
    assert expected == second_row[0]
    expected = models.Process(
        'sample collection', 'sample collection-5-2', date(2018, 2, 2),
        'John Doe', (), (), None, None)
    assert expected == second_row[1]
    expected = models.Material(
        'Sample Name', 'sample-0815-T1', None, (), (), (), None)
    assert expected == second_row[2]


def test_study_reader_small_study(
        small_investigation_file, small_study_file):
    """Use ``StudyReader`` to read in small study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    reader = StudyReader.from_stream(investigation, "S1", small_study_file)
    assert 7 == len(reader.header)

    # Read study
    study = reader.read()

    # Check results
    assert str(study.file).endswith('data/i_small/s_small.txt')
    assert 7 == len(study.header)
    assert 7 == len(study.materials)
    assert 4 == len(study.processes)
    assert 8 == len(study.arcs)

    characteristics1 = models.Characteristics(
        name='organism',
        value=models.OntologyTermRef(
            name='Mus musculus',
            accession='http://purl.bioontology.org/ontology/NCBITAXON/10090',
            ontology_name='NCBITAXON'),
        unit=None)
    characteristics2 = models.Characteristics(
        name='organism',
        value='Mus musculus',
        unit=None)
    characteristics3 = models.Characteristics(
        name='organism',
        value=None,
        unit=None)

    expected = models.Material(
        'Source Name', 'source-0815', None, (characteristics1,), (), (), None)
    assert expected == study.materials['source-0815']
    expected = models.Material(
        'Source Name', 'source-0816', None, (characteristics2,), (), (), None)
    assert expected == study.materials['source-0816']
    expected = models.Material(
        'Source Name', 'source-0817', None, (characteristics3,), (), (), None)
    assert expected == study.materials['source-0817']
    expected = models.Material(
        'Sample Name', 'sample-0815-N1', None, (), (), (), None)
    assert expected == study.materials['sample-0815-N1']
    expected = models.Material(
        'Sample Name', 'sample-0815-T1', None, (), (), (), None)
    assert expected == study.materials['sample-0815-T1']
    expected = models.Material(
        'Sample Name', 'sample-0816-T1', None, (), (), (), None)
    assert expected == study.materials['sample-0816-T1']
    expected = models.Material(
        'Sample Name', 'sample-0817-T1', None, (), (), (), None)
    assert expected == study.materials['sample-0817-T1']

    expected = models.Process(
        'sample collection', 'sample collection-5-1', date(2018, 2, 2),
        'John Doe', (), (), None, None)
    assert expected == study.processes['sample collection-5-1']
    expected = models.Process(
        'sample collection', 'sample collection-5-2', date(2018, 2, 2),
        'John Doe', (), (), None, None)
    assert expected == study.processes['sample collection-5-2']
    expected = models.Process(
        'sample collection', 'sample collection-5-3', date(2018, 2, 2),
        'John Doe', (), (), None, None)
    assert expected == study.processes['sample collection-5-3']

    expected = (
        models.Arc('source-0815', 'sample collection-5-1'),
        models.Arc('sample collection-5-1', 'sample-0815-N1'),
        models.Arc('source-0815', 'sample collection-5-2'),
        models.Arc('sample collection-5-2', 'sample-0815-T1'),
        models.Arc('source-0816', 'sample collection-5-3'),
        models.Arc('sample collection-5-3', 'sample-0816-T1'),
        models.Arc('source-0817', 'sample collection-5-4'),
        models.Arc('sample collection-5-4', 'sample-0817-T1'),
    )
    assert expected == study.arcs

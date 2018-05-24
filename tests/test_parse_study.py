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
        investigation, investigation.studies[0], "S1", minimal_study_file)
    assert 3 == len(row_reader.header)

    # Read all rows in study
    rows = list(row_reader.read())

    # Check results
    assert 1 == len(rows)
    first_row = rows[0]

    assert 3 == len(first_row)

    expected = models.Material(
        'Source Name', 'S1-source-0815', '0815', None, (), (), (), None)
    assert expected == first_row[0]
    expected = models.Process(
        'sample collection', 'S1-sample collection-2-1', None, None, None,
        (), (), None, None)
    assert expected == first_row[1]
    expected = models.Material(
        'Sample Name', 'S1-sample-0815-N1', '0815-N1', None, (), (), (), None)
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
        investigation, investigation.studies[0], "S1", minimal_study_file)
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
        'Source Name', 'S1-source-0815', '0815', None, (), (), (), None)
    assert expected == study.materials['S1-source-0815']
    expected = models.Material(
        'Sample Name', 'S1-sample-0815-N1', '0815-N1', None, (), (), (), None)
    assert expected == study.materials['S1-sample-0815-N1']

    expected = models.Process(
        'sample collection', 'S1-sample collection-2-1', None,
        None, None, (), (), None, None)
    assert expected == study.processes['S1-sample collection-2-1']

    expected = (models.Arc('S1-source-0815', 'S1-sample collection-2-1'),
                models.Arc('S1-sample collection-2-1', 'S1-sample-0815-N1'))
    assert expected == study.arcs


def test_study_row_reader_small_study(
        small_investigation_file, small_study_file):
    """Use ``StudyRowReader`` to read in small study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = StudyRowReader.from_stream(
        investigation, investigation.studies[0], "S1", small_study_file)
    assert 13 == len(row_reader.header)

    # Read all rows in study
    rows = list(row_reader.read())

    # Check results
    assert 4 == len(rows)
    first_row = rows[0]
    second_row = rows[1]

    assert 3 == len(first_row)

    unit = models.OntologyTermRef(
        name='day',
        accession='http://purl.obolibrary.org/obo/UO_0000033',
        ontology_name='UO'
    )

    characteristics = (
        models.Characteristics(
            name='organism',
            value=models.OntologyTermRef(
                name='Mus musculus',
                accession='http://purl.bioontology.org/ontology/'
                          'NCBITAXON/10090',
                ontology_name='NCBITAXON'),
            unit=None),
        models.Characteristics(name='age', value='90', unit=unit))

    expected = models.Material(
        'Source Name', 'S1-source-0815', '0815',
        None, characteristics, (), (), None)
    assert expected == first_row[0]
    expected = models.Process(
        'sample collection', 'S1-sample collection-9-1',  None,
        date(2018, 2, 2), 'John Doe',
        (models.ParameterValue('instrument', 'scalpel', None), ),
        (), None, None)
    assert expected == first_row[1]
    expected = models.Material(
        'Sample Name', 'S1-sample-0815-N1', '0815-N1',
        None, (models.Characteristics('status', '0', None), ), (),
        (models.FactorValue('treatment', 'yes', None), ), None)
    assert expected == first_row[2]

    assert 3 == len(second_row)
    expected = models.Material(
        'Source Name', 'S1-source-0815', '0815',
        None, characteristics, (), (), None)
    assert expected == second_row[0]
    expected = models.Process(
        'sample collection', 'S1-sample collection-9-2', None,
        date(2018, 2, 2), 'John Doe',
        (models.ParameterValue('instrument', 'scalpel', None), ),
        (), None, None)
    assert expected == second_row[1]
    expected = models.Material(
        'Sample Name', 'S1-sample-0815-T1', '0815-T1',
        None,  (models.Characteristics('status', '2', None), ), (),
        (models.FactorValue('treatment', None, None), ), None)
    assert expected == second_row[2]


def test_study_reader_small_study(
        small_investigation_file, small_study_file):
    """Use ``StudyReader`` to read in small study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    reader = StudyReader.from_stream(
        investigation, investigation.studies[0], 'S1', small_study_file)
    assert 13 == len(reader.header)

    # Read study
    study = reader.read()

    # Check results
    assert str(study.file).endswith('data/i_small/s_small.txt')
    assert 13 == len(study.header)
    assert 7 == len(study.materials)
    assert 4 == len(study.processes)
    assert 8 == len(study.arcs)

    unit = models.OntologyTermRef(
        name='day',
        accession='http://purl.obolibrary.org/obo/UO_0000033',
        ontology_name='UO'
    )

    characteristics1 = (
        models.Characteristics(
            name='organism',
            value=models.OntologyTermRef(
                name='Mus musculus',
                accession='http://purl.bioontology.org/ontology/'
                          'NCBITAXON/10090',
                ontology_name='NCBITAXON'),
            unit=None),
        models.Characteristics(name='age', value='90', unit=unit))
    characteristics2 = (
        models.Characteristics(
            name='organism',
            value='Mus musculus',
            unit=None),
        models.Characteristics(name='age', value=None, unit=unit))
    characteristics3 = (
        models.Characteristics(
            name='organism',
            value=None,
            unit=None),
        models.Characteristics(name='age', value='150', unit=unit))

    expected = models.Material(
        'Source Name', 'S1-source-0815', '0815', None,
        characteristics1, (), (), None)
    assert expected == study.materials['S1-source-0815']
    expected = models.Material(
        'Source Name', 'S1-source-0816', '0816', None,
        characteristics2, (), (),  None)
    assert expected == study.materials['S1-source-0816']
    expected = models.Material(
        'Source Name', 'S1-source-0817', '0817', None,
        characteristics3, (), (), None)
    assert expected == study.materials['S1-source-0817']
    expected = models.Material(
        'Sample Name', 'S1-sample-0815-N1', '0815-N1',
        None, (models.Characteristics('status', '0', None), ), (),
        (models.FactorValue("treatment", "yes", None),), None)
    assert expected == study.materials['S1-sample-0815-N1']
    expected = models.Material(
        'Sample Name', 'S1-sample-0815-T1', '0815-T1',
        None, (models.Characteristics('status', '2', None),), (),
        (models.FactorValue("treatment", None, None),), None)
    assert expected == study.materials['S1-sample-0815-T1']
    expected = models.Material(
        'Sample Name', 'S1-sample-0816-T1', '0816-T1',
        None, (models.Characteristics('status', '1', None),), (),
        (models.FactorValue("treatment", "yes", None),), None)
    assert expected == study.materials['S1-sample-0816-T1']
    expected = models.Material(
        'Sample Name', 'S1-Empty Sample Name-13-4', '', None,
        (models.Characteristics('status', None, None),), (),
        (models.FactorValue("treatment", None, None),), None)
    assert expected == study.materials['S1-Empty Sample Name-13-4']

    expected = models.Process(
        'sample collection', 'S1-sample collection-9-1', None,
        date(2018, 2, 2), 'John Doe',
        (models.ParameterValue('instrument', 'scalpel', None), ),
        (), None, None)
    assert expected == study.processes['S1-sample collection-9-1']
    expected = models.Process(
        'sample collection', 'S1-sample collection-9-2', None,
        date(2018, 2, 2), 'John Doe',
        (models.ParameterValue('instrument', 'scalpel', None), ),
        (), None, None)
    assert expected == study.processes['S1-sample collection-9-2']
    expected = models.Process(
        'sample collection', 'S1-sample collection-9-3', None,
        date(2018, 2, 2), 'John Doe',
        (models.ParameterValue('instrument', 'scalpel', None), ),
        (), None, None)
    assert expected == study.processes['S1-sample collection-9-3']

    expected = (
        models.Arc('S1-source-0815', 'S1-sample collection-9-1'),
        models.Arc('S1-sample collection-9-1', 'S1-sample-0815-N1'),
        models.Arc('S1-source-0815', 'S1-sample collection-9-2'),
        models.Arc('S1-sample collection-9-2', 'S1-sample-0815-T1'),
        models.Arc('S1-source-0816', 'S1-sample collection-9-3'),
        models.Arc('S1-sample collection-9-3', 'S1-sample-0816-T1'),
        models.Arc('S1-source-0817', 'S1-sample collection-9-4'),
        models.Arc('S1-sample collection-9-4', 'S1-Empty Sample Name-13-4'),
    )
    assert expected == study.arcs

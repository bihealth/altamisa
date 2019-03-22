# -*- coding: utf-8 -*-
"""Tests for parsing ISA study files"""


from datetime import date

import pytest  # noqa # pylint: disable=unused-import
import os

from altamisa.constants import table_headers
from altamisa.isatab import models
from altamisa.isatab import InvestigationReader, StudyRowReader, StudyReader


def test_study_row_reader_minimal_study(minimal_investigation_file, minimal_study_file):
    """Use ``StudyRowReader`` to read in minimal study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = StudyRowReader.from_stream(
        investigation, investigation.studies[0], "S1", minimal_study_file
    )
    assert 3 == len(row_reader.header)

    # Read all rows in study
    rows = list(row_reader.read())

    # Check results
    assert 1 == len(rows)
    first_row = rows[0]

    assert 3 == len(first_row)

    expected = models.Material(
        "Source Name",
        "S1-source-0815",
        "0815",
        None,
        (),
        (),
        (),
        None,
        None,
        [table_headers.SOURCE_NAME],
    )
    assert expected == first_row[0]
    expected = models.Process(
        "sample collection",
        "S1-sample collection-2-1",
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
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (),
        (),
        (),
        None,
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == first_row[2]


def test_study_reader_minimal_study(minimal_investigation_file, minimal_study_file):
    """Use ``StudyReader`` to read in minimal study file.

    Using the ``StudyReader`` instead of the ``StudyRowReader`` gives us
    ``Study`` objects instead of just the row-wise nodes.
    """
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()

    # Create new row reader and check read headers
    reader = StudyReader.from_stream(
        investigation, investigation.studies[0], "S1", minimal_study_file
    )
    assert 3 == len(reader.header)

    # Read study
    study = reader.read()

    # Check results
    assert os.path.normpath(str(study.file)).endswith(
        os.path.normpath("data/i_minimal/s_minimal.txt")
    )
    assert 3 == len(study.header)
    assert 2 == len(study.materials)
    assert 1 == len(study.processes)
    assert 2 == len(study.arcs)

    expected = models.Material(
        "Source Name",
        "S1-source-0815",
        "0815",
        None,
        (),
        (),
        (),
        None,
        None,
        [table_headers.SOURCE_NAME],
    )
    assert expected == study.materials["S1-source-0815"]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (),
        (),
        (),
        None,
        None,
        [table_headers.SAMPLE_NAME],
    )
    assert expected == study.materials["S1-sample-0815-N1"]

    expected = models.Process(
        "sample collection",
        "S1-sample collection-2-1",
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
    assert expected == study.processes["S1-sample collection-2-1"]

    expected = (
        models.Arc("S1-source-0815", "S1-sample collection-2-1"),
        models.Arc("S1-sample collection-2-1", "S1-sample-0815-N1"),
    )
    assert expected == study.arcs


def test_study_row_reader_small_study(small_investigation_file, small_study_file):
    """Use ``StudyRowReader`` to read in small study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    row_reader = StudyRowReader.from_stream(
        investigation, investigation.studies[0], "S1", small_study_file
    )
    assert 13 == len(row_reader.header)

    # Read all rows in study
    rows = list(row_reader.read())

    # Check results
    assert 5 == len(rows)
    first_row = rows[0]
    second_row = rows[1]
    third_row = rows[2]

    assert 3 == len(second_row)

    headers_source = [
        table_headers.SOURCE_NAME,
        table_headers.CHARACTERISTICS + "[organism]",
        table_headers.TERM_SOURCE_REF,
        table_headers.TERM_ACCESSION_NUMBER,
        table_headers.CHARACTERISTICS + "[age]",
        table_headers.UNIT,
        table_headers.TERM_SOURCE_REF,
        table_headers.TERM_ACCESSION_NUMBER,
    ]
    headers_collection = [
        table_headers.PROTOCOL_REF,
        table_headers.PARAMETER_VALUE + "[instrument]",
        table_headers.PERFORMER,
        table_headers.DATE,
    ]
    headers_sample = [
        table_headers.SAMPLE_NAME,
        table_headers.CHARACTERISTICS + "[status]",
        table_headers.FACTOR_VALUE + "[treatment]",
    ]

    unit = models.OntologyTermRef(
        name="day", accession="http://purl.obolibrary.org/obo/UO_0000033", ontology_name="UO"
    )

    characteristics1 = (
        models.Characteristics(
            name="organism",
            value=[
                models.OntologyTermRef(
                    name="Mus musculus",
                    accession="http://purl.bioontology.org/ontology/NCBITAXON/10090",
                    ontology_name="NCBITAXON",
                ),
                models.OntologyTermRef(
                    name="Homo sapiens",
                    accession="http://purl.bioontology.org/ontology/NCBITAXON/9606",
                    ontology_name="NCBITAXON",
                ),
            ],
            unit=None,
        ),
        models.Characteristics(name="age", value=["90"], unit=unit),
    )

    expected = models.Material(
        "Source Name",
        "S1-source-0814",
        "0814",
        None,
        characteristics1,
        (),
        (),
        None,
        None,
        headers_source,
    )
    assert expected == first_row[0]

    characteristics2 = (
        models.Characteristics(
            name="organism",
            value=[
                models.OntologyTermRef(
                    name="Mus musculus",
                    accession="http://purl.bioontology.org/ontology/NCBITAXON/10090",
                    ontology_name="NCBITAXON",
                )
            ],
            unit=None,
        ),
        models.Characteristics(name="age", value=["90"], unit=unit),
    )

    expected = models.Material(
        "Source Name",
        "S1-source-0815",
        "0815",
        None,
        characteristics2,
        (),
        (),
        None,
        None,
        headers_source,
    )
    assert expected == second_row[0]
    expected = models.Process(
        "sample collection",
        "S1-sample collection-9-2",
        None,
        None,
        date(2018, 2, 2),
        "John Doe",
        (models.ParameterValue("instrument", ["scalpel"], None),),
        (),
        None,
        None,
        None,
        headers_collection,
    )
    assert expected == second_row[1]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (models.Characteristics("status", ["0"], None),),
        (),
        (models.FactorValue("treatment", "yes", None),),
        None,
        None,
        headers_sample,
    )
    assert expected == second_row[2]

    assert 3 == len(third_row)
    expected = models.Material(
        "Source Name",
        "S1-source-0815",
        "0815",
        None,
        characteristics2,
        (),
        (),
        None,
        None,
        headers_source,
    )
    assert expected == third_row[0]
    expected = models.Process(
        "sample collection",
        "S1-sample collection-9-3",
        None,
        None,
        date(2018, 2, 2),
        "John Doe",
        (models.ParameterValue("instrument", ["scalpel type A", "scalpel type B"], None),),
        (),
        None,
        None,
        None,
        headers_collection,
    )
    assert expected == third_row[1]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-T1",
        "0815-T1",
        None,
        (models.Characteristics("status", ["2"], None),),
        (),
        (models.FactorValue("treatment", "", None),),
        None,
        None,
        headers_sample,
    )
    assert expected == third_row[2]


def test_study_reader_small_study(small_investigation_file, small_study_file):
    """Use ``StudyReader`` to read in small study file."""
    # Load investigation (tested elsewhere)
    investigation = InvestigationReader.from_stream(small_investigation_file).read()

    # Create new row reader and check read headers
    reader = StudyReader.from_stream(
        investigation, investigation.studies[0], "S1", small_study_file
    )
    assert 13 == len(reader.header)

    # Read study
    study = reader.read()

    # Check results
    assert os.path.normpath(str(study.file)).endswith(os.path.normpath("data/i_small/s_small.txt"))
    assert 13 == len(study.header)
    assert 9 == len(study.materials)
    assert 5 == len(study.processes)
    assert 10 == len(study.arcs)

    headers_source = [
        table_headers.SOURCE_NAME,
        table_headers.CHARACTERISTICS + "[organism]",
        table_headers.TERM_SOURCE_REF,
        table_headers.TERM_ACCESSION_NUMBER,
        table_headers.CHARACTERISTICS + "[age]",
        table_headers.UNIT,
        table_headers.TERM_SOURCE_REF,
        table_headers.TERM_ACCESSION_NUMBER,
    ]
    headers_collection = [
        table_headers.PROTOCOL_REF,
        table_headers.PARAMETER_VALUE + "[instrument]",
        table_headers.PERFORMER,
        table_headers.DATE,
    ]
    headers_sample = [
        table_headers.SAMPLE_NAME,
        table_headers.CHARACTERISTICS + "[status]",
        table_headers.FACTOR_VALUE + "[treatment]",
    ]

    unit = models.OntologyTermRef(
        name="day", accession="http://purl.obolibrary.org/obo/UO_0000033", ontology_name="UO"
    )

    characteristics1 = (
        models.Characteristics(
            name="organism",
            value=[
                models.OntologyTermRef(
                    name="Mus musculus",
                    accession="http://purl.bioontology.org/ontology/" "NCBITAXON/10090",
                    ontology_name="NCBITAXON",
                )
            ],
            unit=None,
        ),
        models.Characteristics(name="age", value=["90"], unit=unit),
    )
    characteristics2 = (
        models.Characteristics(
            name="organism", value=[models.OntologyTermRef("Mus musculus", "", "")], unit=None
        ),
        models.Characteristics(name="age", value=[""], unit=unit),
    )
    characteristics3 = (
        models.Characteristics(
            name="organism", value=[models.OntologyTermRef(None, None, None)], unit=None
        ),
        models.Characteristics(name="age", value=["150"], unit=unit),
    )

    expected = models.Material(
        "Source Name",
        "S1-source-0815",
        "0815",
        None,
        characteristics1,
        (),
        (),
        None,
        None,
        headers_source,
    )
    assert expected == study.materials["S1-source-0815"]
    expected = models.Material(
        "Source Name",
        "S1-source-0816",
        "0816",
        None,
        characteristics2,
        (),
        (),
        None,
        None,
        headers_source,
    )
    assert expected == study.materials["S1-source-0816"]
    expected = models.Material(
        "Source Name",
        "S1-source-0817",
        "0817",
        None,
        characteristics3,
        (),
        (),
        None,
        None,
        headers_source,
    )
    assert expected == study.materials["S1-source-0817"]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-N1",
        "0815-N1",
        None,
        (models.Characteristics("status", ["0"], None),),
        (),
        (models.FactorValue("treatment", "yes", None),),
        None,
        None,
        headers_sample,
    )
    assert expected == study.materials["S1-sample-0815-N1"]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0815-T1",
        "0815-T1",
        None,
        (models.Characteristics("status", ["2"], None),),
        (),
        (models.FactorValue("treatment", "", None),),
        None,
        None,
        headers_sample,
    )
    assert expected == study.materials["S1-sample-0815-T1"]
    expected = models.Material(
        "Sample Name",
        "S1-sample-0816-T1",
        "0816-T1",
        None,
        (models.Characteristics("status", ["1"], None),),
        (),
        (models.FactorValue("treatment", "yes", None),),
        None,
        None,
        headers_sample,
    )
    assert expected == study.materials["S1-sample-0816-T1"]
    expected = models.Material(
        "Sample Name",
        "S1-Empty Sample Name-13-5",
        "",
        None,
        (models.Characteristics("status", [""], None),),
        (),
        (models.FactorValue("treatment", "", None),),
        None,
        None,
        headers_sample,
    )
    assert expected == study.materials["S1-Empty Sample Name-13-5"]

    expected = models.Process(
        "sample collection",
        "S1-sample collection-9-2",
        None,
        None,
        date(2018, 2, 2),
        "John Doe",
        (models.ParameterValue("instrument", ["scalpel"], None),),
        (),
        None,
        None,
        None,
        headers_collection,
    )
    assert expected == study.processes["S1-sample collection-9-2"]
    expected = models.Process(
        "sample collection",
        "S1-sample collection-9-3",
        None,
        None,
        date(2018, 2, 2),
        "John Doe",
        (models.ParameterValue("instrument", ["scalpel type A", "scalpel type B"], None),),
        (),
        None,
        None,
        None,
        headers_collection,
    )
    assert expected == study.processes["S1-sample collection-9-3"]
    expected = models.Process(
        "sample collection",
        "S1-sample collection-9-4",
        None,
        None,
        date(2018, 2, 2),
        "John Doe",
        (models.ParameterValue("instrument", ["scalpel"], None),),
        (),
        None,
        None,
        None,
        headers_collection,
    )
    assert expected == study.processes["S1-sample collection-9-4"]

    expected = (
        models.Arc("S1-source-0814", "S1-sample collection-9-1"),
        models.Arc("S1-sample collection-9-1", "S1-sample-0814-N1"),
        models.Arc("S1-source-0815", "S1-sample collection-9-2"),
        models.Arc("S1-sample collection-9-2", "S1-sample-0815-N1"),
        models.Arc("S1-source-0815", "S1-sample collection-9-3"),
        models.Arc("S1-sample collection-9-3", "S1-sample-0815-T1"),
        models.Arc("S1-source-0816", "S1-sample collection-9-4"),
        models.Arc("S1-sample collection-9-4", "S1-sample-0816-T1"),
        models.Arc("S1-source-0817", "S1-sample collection-9-5"),
        models.Arc("S1-sample collection-9-5", "S1-Empty Sample Name-13-5"),
    )
    assert expected == study.arcs

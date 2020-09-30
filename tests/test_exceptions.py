# -*- coding: utf-8 -*-
"""Tests for ISA exceptions"""


import pytest

from altamisa.exceptions import ParseIsatabException
from altamisa.isatab import AssayReader, InvestigationReader


# Test header exceptions ---------------------------------------------------------------------------


def test_header_exception_simple_header_not_allowed(assay_file_exception_simple_header_not_allowed):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_simple_header_not_allowed)
    msg = 'Header "Source Name" not allowed in assay.'
    assert msg == str(excinfo.value)


def test_header_exception_labeled_header_not_allowed(
    assay_file_exception_labeled_header_not_allowed
):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_labeled_header_not_allowed)
    msg = 'Header "Factor Value" not allowed in assay.'
    assert msg == str(excinfo.value)


def test_header_exception_unknown_header(assay_file_exception_unknown_header):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_unknown_header)
    msg = 'Header "Test Name" unknown, processing unclear'
    assert msg == str(excinfo.value)


def test_header_exception_term_source_ref_next_column(
    assay_file_exception_term_source_ref_next_column
):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_term_source_ref_next_column)
    msg = 'Expected column "Term Accession Number" after seeing "Term Source REF"'
    assert msg == str(excinfo.value)


def test_header_exception_term_source_ref_stop_iteration(
    assay_file_exception_term_source_ref_stop_iteration
):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_term_source_ref_stop_iteration)
    msg = 'Expected one more column on seeing "Term Source REF"'
    assert msg == str(excinfo.value)


def test_header_exception_labeled_header_format(assay_file_exception_labeled_header_format):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_labeled_header_format)
    msg = "Problem parsing labeled header CharacteristicsWithoutBrackets"
    assert msg == str(excinfo.value)


def test_header_exception_investigation_comment_format(investigation_file_exception_comment_format):
    with pytest.raises(ParseIsatabException) as excinfo:
        InvestigationReader.from_stream(investigation_file_exception_comment_format).read()
    msg = 'Problem parsing comment header "Comment [Test]"'
    assert msg == str(excinfo.value)


def test_header_exception_duplicated_header(assay_file_exception_duplicated_header):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_duplicated_header).read()
    msg = "Found duplicated column types in header of study S1 assay A1: Characteristics[Organism]"
    assert msg == str(excinfo.value)


# Test assay and study parsing exceptions ----------------------------------------------------------


def test_parsing_exception_invalid_column_type(assay_file_exception_invalid_column_type):
    with pytest.raises(ParseIsatabException) as excinfo:
        AssayReader.from_stream("S1", "A1", assay_file_exception_invalid_column_type).read()
    msg = (
        "Invalid column type occured \"Parameter Value\" not in ('Material Type', "
        "'Characteristics', 'Comment', 'Factor Value', 'Label', 'Term Source REF', 'Unit')"
    )
    assert msg == str(excinfo.value)

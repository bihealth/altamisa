# -*- coding: utf-8 -*-
"""Tests for writing ISA investigation files"""


import filecmp
import pytest

from altamisa.exceptions import (
    CriticalIsaValidationWarning,
    IsaWarning,
    ModerateIsaValidationWarning,
    ParseIsatabWarning,
    WriteIsatabWarning,
)
from altamisa.isatab import InvestigationReader, InvestigationWriter, InvestigationValidator


# Tests with one-time reading and writing


def test_write_minimal_investigation(minimal_investigation_file, tmp_path):
    # Read Investigation from file-like object
    with pytest.warns(IsaWarning) as record:
        investigation = InvestigationReader.from_stream(minimal_investigation_file).read()
        InvestigationValidator(investigation).validate()
    # Check warnings
    assert 2 == len(record)
    # Write Investigation to temporary file
    path = tmp_path / "i_minimal.txt"
    with pytest.warns(IsaWarning) as record:
        with open(path, "wt") as file:
            InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Check warnings
    assert 6 == len(record)
    msg = "No reference headers available for section STUDY PUBLICATIONS. Applying default order."
    assert record[3].category == WriteIsatabWarning
    assert str(record[3].message) == msg
    # Compare input and output
    assert filecmp.cmp(minimal_investigation_file.name, path, shallow=False)


def test_write_small_investigation(small_investigation_file, tmp_path):
    # Read Investigation from file-like object
    with pytest.warns(IsaWarning) as record:
        investigation = InvestigationReader.from_stream(small_investigation_file).read()
        InvestigationValidator(investigation).validate()
    # Check warnings
    assert 2 == len(record)
    # Write Investigation to temporary file
    path = tmp_path / "i_small.txt"
    with pytest.warns(IsaWarning) as record:
        with open(path, "wt") as file:
            InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Check warnings
    assert 4 == len(record)
    msg = (
        "No reference headers available for section INVESTIGATION CONTACTS. Applying default order."
    )
    assert record[1].category == WriteIsatabWarning
    assert str(record[1].message) == msg
    # Compare input and output
    assert filecmp.cmp(small_investigation_file.name, path, shallow=False)


def test_write_comment_investigation(comment_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(comment_investigation_file).read()
    InvestigationValidator(investigation).validate()
    # Write Investigation to temporary file
    path = tmp_path / "i_comments.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(comment_investigation_file.name, path, shallow=False)


def test_write_full2_investigation(full2_investigation_file, tmp_path):
    # Read Investigation from file-like object
    with pytest.warns(IsaWarning) as record:
        investigation = InvestigationReader.from_stream(full2_investigation_file).read()
        InvestigationValidator(investigation).validate()
    # Check warnings
    assert 3 == len(record)
    msg = "Study with incomplete minimal information (ID and path):\nID:\t\nTitle:\t\nPath:\t"
    assert record[0].category == CriticalIsaValidationWarning
    assert str(record[0].message) == msg
    msg = "Study without title:\nID:\t\nTitle:\t\nPath:\t"
    assert record[1].category == ModerateIsaValidationWarning
    assert str(record[1].message) == msg
    msg = (
        "Assay with incomplete minimal information (path, measurement and technology type):\n"
        "Path:\t\n"
        "Measurement Type:\tmetabolite profiling\n"
        "Technology Type:\tmass spectrometry\n"
        "Technology Platform:\tLC-MS/MS"
    )
    assert record[2].category == CriticalIsaValidationWarning
    assert str(record[2].message) == msg
    # Write Investigation to temporary file
    path = tmp_path / "i_fullinvest2.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(full2_investigation_file.name, path, shallow=False)


def test_write_BII_I_2_investigation(BII_I_2_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(BII_I_2_investigation_file).read()
    InvestigationValidator(investigation).validate()
    # Write Investigation to temporary file
    path = tmp_path / "i_investigation.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, quote='"', lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(BII_I_2_investigation_file.name, path, shallow=False)


# Tests with second reading and writing for normalization


def test_write_assays_investigation(assays_investigation_file, tmp_path):
    # Read Investigation from file-like object
    with pytest.warns(IsaWarning) as record:
        investigation = InvestigationReader.from_stream(assays_investigation_file).read()
        InvestigationValidator(investigation).validate()
    # Check warnings
    assert 7 == len(record)
    # Write Investigation to temporary file
    path1 = tmp_path / "i_assays.txt"
    with pytest.warns(IsaWarning) as record:
        with open(path1, "wt") as file:
            InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Check warnings
    assert 12 == len(record)
    # Read Investigation from temporary file
    with open(path1, "rt") as file:
        reader = InvestigationReader.from_stream(file)
        investigation = reader.read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()
    # Check warnings
    assert 5 == len(record)
    # Write Investigation to second temporary file
    path2 = tmp_path / "i_assays_2.txt"
    with pytest.warns(IsaWarning) as record:
        with open(path2, "wt") as file:
            InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Check warnings
    assert 12 == len(record)
    # Compare input and output
    assert filecmp.cmp(path1, path2, shallow=False)


def test_write_full_investigation(full_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(full_investigation_file).read()
    InvestigationValidator(investigation).validate()
    # Write Investigation to temporary file
    path1 = tmp_path / "i_fullinvest.txt"
    with open(path1, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Read Investigation from temporary file
    with open(path1, "rt") as file:
        reader = InvestigationReader.from_stream(file)
        investigation = reader.read()
    # Write Investigation to second temporary file
    path2 = tmp_path / "i_fullinvest_2.txt"
    with open(path2, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(path1, path2, shallow=False)


def test_write_BII_I_1_investigation(BII_I_1_investigation_file, tmp_path):
    # Read Investigation from file-like object
    with pytest.warns(IsaWarning) as record:
        investigation = InvestigationReader.from_stream(BII_I_1_investigation_file).read()
        InvestigationValidator(investigation).validate()
    # Check warnings
    assert 1 == len(record)
    msg = "Skipping empty ontology source: , , , "
    assert record[0].category == ParseIsatabWarning
    assert str(record[0].message) == msg
    # Write Investigation to temporary file
    path1 = tmp_path / "i_investigation.txt"
    with open(path1, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Read Investigation from temporary file
    with open(path1, "rt") as file:
        reader = InvestigationReader.from_stream(file)
        investigation = reader.read()
    # Write Investigation to second temporary file
    path2 = tmp_path / "i_investigation_2.txt"
    with open(path2, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(path1, path2, shallow=False)

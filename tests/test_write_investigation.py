# -*- coding: utf-8 -*-
"""Tests for writing ISA investigation files"""


import filecmp

from altamisa.isatab import InvestigationReader, InvestigationWriter


# Tests with one-time reading and writing


def test_parse_minimal_investigation(minimal_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(minimal_investigation_file).read()
    # Write Investigation to temporary file
    path = tmp_path / "i_minimal.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(minimal_investigation_file.name, path, shallow=False)


def test_parse_small_investigation(small_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(small_investigation_file).read()
    # Write Investigation to temporary file
    path = tmp_path / "i_small.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(small_investigation_file.name, path, shallow=False)


def test_parse_comment_investigation(comment_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(comment_investigation_file).read()
    # Write Investigation to temporary file
    path = tmp_path / "i_comments.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(comment_investigation_file.name, path, shallow=False)


def test_parse_full2_investigation(full2_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(full2_investigation_file).read()
    # Write Investigation to temporary file
    path = tmp_path / "i_fullinvest2.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(full2_investigation_file.name, path, shallow=False)


def test_parse_assays2_investigation(assays2_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(assays2_investigation_file).read()
    # Write Investigation to temporary file
    path = tmp_path / "i_assays2.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(assays2_investigation_file.name, path, shallow=False)


def test_parse_BII_I_2_investigation(BII_I_2_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(BII_I_2_investigation_file).read()
    # Write Investigation to temporary file
    path = tmp_path / "i_investigation.txt"
    with open(path, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, quote='"', lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(BII_I_2_investigation_file.name, path, shallow=False)


# Tests with second reading and writing for normalization


def test_parse_assays_investigation(assays_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(assays_investigation_file).read()
    # Write Investigation to temporary file
    path1 = tmp_path / "i_assays.txt"
    with open(path1, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Read Investigation from temporary file
    with open(path1, "rt") as file:
        reader = InvestigationReader.from_stream(file)
        investigation = reader.read()
    # Write Investigation to second temporary file
    path2 = tmp_path / "i_assays_2.txt"
    with open(path2, "wt") as file:
        InvestigationWriter.from_stream(investigation, file, lineterminator="\n").write()
    # Compare input and output
    assert filecmp.cmp(path1, path2, shallow=False)


def test_parse_full_investigation(full_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(full_investigation_file).read()
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


def test_parse_BII_I_1_investigation(BII_I_1_investigation_file, tmp_path):
    # Read Investigation from file-like object
    investigation = InvestigationReader.from_stream(BII_I_1_investigation_file).read()
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

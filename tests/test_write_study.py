# -*- coding: utf-8 -*-
"""Tests for writing ISA study files"""


import filecmp
import os

import pytest
from syrupy.assertion import SnapshotAssertion

from altamisa.exceptions import IsaWarning
from altamisa.isatab import (
    InvestigationReader,
    InvestigationValidator,
    StudyReader,
    StudyValidator,
    StudyWriter,
)


# Helper to load, write and compare studies
def _parse_write_assert(investigation_file, tmp_path, quote=None):
    # Load investigation
    investigation = InvestigationReader.from_stream(investigation_file).read()
    InvestigationValidator(investigation).validate()
    directory = os.path.normpath(os.path.dirname(investigation_file.name))
    # Iterate studies
    for s, study_info in enumerate(investigation.studies):
        # Load study
        if not study_info.info.path:
            raise ValueError(f"Study {study_info} has no path")
        path_in = os.path.join(directory, study_info.info.path)
        with open(path_in, "rt") as inputf:
            study = StudyReader.from_stream(f"S{s + 1}", inputf).read()
        StudyValidator(investigation, study_info, study).validate()
        # Write study to temporary file
        path_out = tmp_path / study_info.info.path
        with open(path_out, "wt", newline="") as file:
            StudyWriter.from_stream(study, file, quote=quote).write()
        assert filecmp.cmp(path_in, path_out, shallow=False)


def test_study_writer_minimal(minimal_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert(minimal_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_study_writer_minimal2(minimal2_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert(minimal2_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_study_writer_small(small_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert(small_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_study_writer_small2(small2_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert(small2_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_study_writer_BII_I_1(BII_I_1_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert(BII_I_1_investigation_file, tmp_path, quote='"')
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_study_writer_gelelect(gelelect_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert(gelelect_investigation_file, tmp_path, quote='"')
    # Check warnings
    assert snapshot == [str(r.category) for r in record]
    assert snapshot == [str(r.message) for r in record]

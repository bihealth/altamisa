# -*- coding: utf-8 -*-
"""Tests for writing ISA assay files"""


import filecmp
import os

import pytest
from syrupy.assertion import SnapshotAssertion

from altamisa.exceptions import IsaWarning
from altamisa.isatab import (
    AssayReader,
    AssayValidator,
    AssayWriter,
    InvestigationReader,
    InvestigationValidator,
)


# Helper to load, write and compare assays
def _parse_write_assert_assay(investigation_file, tmp_path, quote=None, normalize=False, skip=None):
    # Load investigation
    investigation = InvestigationReader.from_stream(investigation_file).read()
    InvestigationValidator(investigation).validate()
    directory = os.path.normpath(os.path.dirname(investigation_file.name))
    # Iterate assays
    for s, study_info in enumerate(investigation.studies):
        for a, assay_info in enumerate(study_info.assays):
            if skip and str(assay_info.path) in skip:
                continue
            # Load assay
            if not assay_info.path:
                raise ValueError(f"Assay {assay_info} has no path")
            path_in = os.path.join(directory, assay_info.path)
            with open(path_in, "rt") as inputf:
                assay = AssayReader.from_stream(f"S{s + 1}", f"A{a + 1}", inputf).read()
            AssayValidator(investigation, study_info, assay_info, assay).validate()
            # Write assay to temporary file
            path_out = tmp_path / assay_info.path
            with open(path_out, "wt", newline="") as file:
                AssayWriter.from_stream(assay, file, quote=quote).write()
            if normalize:
                # Read and write assay again
                path_in = path_out
                with open(path_out, "rt") as inputf:
                    assay = AssayReader.from_stream(f"S{s + 1}", f"A{a + 1}", inputf).read()
                AssayValidator(investigation, study_info, assay_info, assay).validate()
                path_out = tmp_path / (assay_info.path.name + "_b")
                with open(path_out, "wt", newline="") as file:
                    AssayWriter.from_stream(assay, file, quote=quote).write()
            assert filecmp.cmp(path_in, path_out, shallow=False)


def test_assay_writer_minimal_assay(
    minimal_investigation_file, tmp_path, snapshot: SnapshotAssertion
):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert_assay(minimal_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_assay_writer_minimal2_assay(
    minimal2_investigation_file, tmp_path, snapshot: SnapshotAssertion
):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert_assay(minimal2_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_assay_writer_small_assay(small_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert_assay(small_investigation_file, tmp_path)
    # Check warnings
    assert snapshot == [str(r.category) for r in record]
    assert snapshot == [str(r.message) for r in record]


def test_assay_writer_small2_assay(
    small2_investigation_file, tmp_path, snapshot: SnapshotAssertion
):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert_assay(small2_investigation_file, tmp_path, normalize=True)
    # Check warnings
    assert snapshot == [str(r.message) for r in record]


def test_assay_writer_BII_I_1(BII_I_1_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    # skipping proteome assay, because it's missing a lot of splits and pools
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert_assay(
            BII_I_1_investigation_file, tmp_path, quote='"', skip=["a_proteome.txt"]
        )
    # Check warnings
    # investigation
    records_skip_ontology = 1
    # a_metabolome + a_microarray + a_transcriptome
    records_assay_sample_meta = 92 + 0 + 0
    records_ms_assay_name = 111 + 0 + 0
    records_scan_name = 0 + 14 + 48
    records_normalization_name = 0 + 0 + 1
    records_data_transformation_name = 0 + 1 + 0
    assert (
        records_skip_ontology
        + records_assay_sample_meta
        + records_ms_assay_name
        + records_scan_name
        + records_normalization_name
        + records_data_transformation_name
        == len(record)
    )
    assert snapshot == [str(r.category) for r in record]
    assert snapshot == [str(r.message) for r in record]


def test_assay_writer_gelelect(gelelect_investigation_file, tmp_path, snapshot: SnapshotAssertion):
    with pytest.warns(IsaWarning) as record:
        _parse_write_assert_assay(gelelect_investigation_file, tmp_path, quote='"')
    assert snapshot == [str(r.category) for r in record]
    assert snapshot == [str(r.message) for r in record]

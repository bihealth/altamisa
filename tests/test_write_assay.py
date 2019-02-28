# -*- coding: utf-8 -*-
"""Tests for writing ISA assay files"""


import filecmp
import os
import pytest  # noqa # pylint: disable=unused-import

from altamisa.isatab import InvestigationReader, AssayReader, AssayWriter
from .conftest import sort_file


# Helper to load, write and compare assays
def _parse_write_assert_assay(investigation_file, tmp_path, quote=None, normalize=False):
    # Load investigation
    investigation = InvestigationReader.from_stream(investigation_file).read()
    directory = os.path.normpath(os.path.dirname(investigation_file.name))
    # Iterate assays
    for s, study_info in enumerate(investigation.studies):
        for a, assay_info in enumerate(study_info.assays.values()):
            # Load assay
            path_in = os.path.join(directory, assay_info.path)
            with open(path_in, "rt") as inputf:
                assay = AssayReader.from_stream(
                    investigation,
                    study_info,
                    assay_info,
                    "S{}".format(s + 1),
                    "A{}".format(a + 1),
                    inputf,
                ).read()
            # Write assay to temporary file
            path_out = tmp_path / assay_info.path
            with open(path_out, "wt") as file:
                AssayWriter.from_stream(assay, file, study_info.factors, quote=quote).write()
            if normalize:
                # Read and write assay again
                path_in = path_out
                with open(path_out, "rt") as inputf:
                    assay = AssayReader.from_stream(
                        investigation,
                        study_info,
                        assay_info,
                        "S{}".format(s + 1),
                        "A{}".format(a + 1),
                        inputf,
                    ).read()
                path_out = tmp_path / (assay_info.path.name + "_b")
                with open(path_out, "wt") as file:
                    AssayWriter.from_stream(assay, file, study_info.factors, quote=quote).write()
            # Sort and compare input and output
            path_in_s = tmp_path / (assay_info.path.name + ".in.sorted")
            path_out_s = tmp_path / (assay_info.path.name + ".out.sorted")
            assert filecmp.cmp(
                sort_file(path_in, path_in_s), sort_file(path_out, path_out_s), shallow=False
            )


def test_assay_writer_minimal_assay(minimal_investigation_file, tmp_path):
    _parse_write_assert_assay(minimal_investigation_file, tmp_path)


def test_assay_writer_minimal2_assay(minimal2_investigation_file, tmp_path):
    _parse_write_assert_assay(minimal2_investigation_file, tmp_path)


def test_assay_writer_small_assay(small_investigation_file, tmp_path):
    _parse_write_assert_assay(small_investigation_file, tmp_path)


def test_assay_writer_small2_assay(small2_investigation_file, tmp_path):
    _parse_write_assert_assay(small2_investigation_file, tmp_path, normalize=True)


def test_assay_writer_gelelect(gelelect_investigation_file, tmp_path):
    _parse_write_assert_assay(gelelect_investigation_file, tmp_path, quote='"')

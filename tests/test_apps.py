# -*- coding: utf-8 -*-
"""Smoke tests for the apps"""

import os.path

import pytest
from syrupy.assertion import SnapshotAssertion
from typer.testing import CliRunner

from altamisa.apps import isatab2dot, isatab2isatab, isatab_validate
from altamisa.exceptions import IsaWarning

runner = CliRunner()


def test_isatab_validate(snapshot: SnapshotAssertion):
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_warnings", "i_warnings.txt")
    argv = ["--input-investigation-file", i_file, "--show-duplicate-warnings"]

    with pytest.warns(IsaWarning) as record:
        result = runner.invoke(isatab_validate.app, argv)
        assert result.exit_code == 0

    assert snapshot == [str(r.message) for r in record]


def test_isatab2isatab(tmpdir, snapshot: SnapshotAssertion):
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_minimal", "i_minimal.txt")
    argv = [
        "--input-investigation-file",
        i_file,
        "--output-investigation-file",
        str(tmpdir.mkdir("i_minimal").join("i_minimal.txt")),
        "--quotes",
        '"',
    ]

    with pytest.warns(IsaWarning) as record:
        result = runner.invoke(isatab2isatab.app, argv)
        assert result.exit_code == 0

    assert snapshot == [str(r.message) for r in record]


def test_isatab2isatab_input_is_output(tmpdir, snapshot: SnapshotAssertion):
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_minimal", "i_minimal.txt")
    argv = [
        "--input-investigation-file",
        i_file,
        "--output-investigation-file",
        i_file,
        "--quotes",
        '"',
    ]

    result = runner.invoke(isatab2isatab.app, argv)
    assert result.exit_code == 1
    assert snapshot == str(result)


def test_isatab2dot(tmpdir):
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_minimal", "i_minimal.txt")
    argv = [
        "--investigation-file",
        i_file,
        "--output-file",
        str(tmpdir.mkdir("dot").join("out.dot")),
    ]

    result = runner.invoke(isatab2dot.app, argv)
    assert result.exit_code == 0

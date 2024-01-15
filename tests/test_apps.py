# -*- coding: utf-8 -*-
"""Smoke tests for the apps"""

import os.path

import pytest
from typer.testing import CliRunner

from altamisa.apps import isatab2dot, isatab2isatab, isatab_validate
from altamisa.exceptions import IsaWarning

runner = CliRunner()


def test_isatab_validate():
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_warnings", "i_warnings.txt")
    argv = ["--input-investigation-file", i_file, "--show-duplicate-warnings"]

    with pytest.warns(IsaWarning) as record:
        result = runner.invoke(isatab_validate.app, argv)
        assert result.exit_code == 0

    assert 17 == len(record)


def test_isatab2isatab(tmpdir):
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

    assert 8 == len(record)


def test_isatab2isatab_input_is_output(tmpdir):
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
    assert "Can't output ISA-tab files to same directory as as input" in str(result)


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

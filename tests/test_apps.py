# -*- coding: utf-8 -*-
"""Smoke tests for the apps"""

import os.path

import pytest
from typer.testing import CliRunner

from altamisa.apps import isatab2dot, isatab2isatab, isatab_validate
from altamisa.exceptions import IsaException, IsaWarning

runner = CliRunner()


def test_isatab_validate():
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_warnings", "i_warnings.txt")
    argv = ["--input-investigation-file", i_file, "--show-duplicate-warnings"]

    with pytest.warns(IsaWarning) as record:
        result = runner.invoke(isatab_validate.app, argv)
        assert result.exit_code == 1
        assert "Warnign" in result.stdout
        assert "Warnign" in result.stderr

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
        assert not isatab2isatab.main(argv)

    assert 10 == len(record)


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

    with pytest.raises(IsaException):
        isatab2isatab.main(argv)


def test_isatab2dot(tmpdir):
    i_file = os.path.join(os.path.dirname(__file__), "data", "i_minimal", "i_minimal.txt")
    argv = [
        "--investigation-file",
        i_file,
        "--output-file",
        str(tmpdir.mkdir("dot").join("out.dot")),
    ]

    assert not isatab2dot.main(argv)

# -*- coding: utf-8 -*-
"""Smoke tests for manual AltamISA model creation"""

import warnings

from docs.examples import create_isa_model


def test_minimal_model_creation(tmp_path):
    with warnings.catch_warnings(record=True) as records:
        create_isa_model.create_and_write(str(tmp_path))

    assert (tmp_path / "i_minimal.txt").exists()
    assert (tmp_path / "s_minimal.txt").exists()
    assert (tmp_path / "a_minimal.txt").exists()

    assert 13 == len(records)

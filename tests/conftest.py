# -*- coding: utf-8 -*-
"""Shared code for the tests.
"""

import io
import os.path

import pytest


@pytest.fixture
def minimal_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/i_minimal.txt")
    return open(path, 'rt')


@pytest.fixture
def minimal_study_file():
    """This file only contains the bare essentials, although ISA-Tab might
    actually forgive us having no ``Process``.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/s_minimal.txt")
    return open(path, 'rt')


@pytest.fixture
def minimal_assay_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/a_minimal.txt")
    return open(path, 'rt')


@pytest.fixture
def small_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small/i_small.txt")
    return open(path, 'rt')


@pytest.fixture
def small_study_file():
    """This file contains a very limited number of annotations and one sample
    that is split (tumor-normal case).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_small/s_small.txt")
    return open(path, 'rt')


@pytest.fixture
def small_assay_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small/a_small.txt")
    return open(path, 'rt')

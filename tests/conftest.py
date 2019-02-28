# -*- coding: utf-8 -*-
"""Shared code for the tests.
"""

import os.path

import pytest  # noqa # pylint: disable=unused-import


# Helper function to sort rows in a file
def sort_file(input_file, output_file):
    with open(input_file, "rt") as f:
        sorted_file = sorted(f)
    with open(output_file, "wt") as f:
        f.writelines(sorted_file)
    return output_file


@pytest.fixture
def minimal_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/i_minimal.txt")
    return open(path, "rt")


@pytest.fixture
def minimal2_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal2/i_minimal2.txt")
    return open(path, "rt")


@pytest.fixture
def minimal_study_file():
    """This file only contains the bare essentials, although ISA-Tab might
    actually forgive us having no ``Process``.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/s_minimal.txt")
    return open(path, "rt")


@pytest.fixture
def minimal_assay_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/a_minimal.txt")
    return open(path, "rt")


@pytest.fixture
def small_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small/i_small.txt")
    return open(path, "rt")


@pytest.fixture
def small_study_file():
    """This file contains a very limited number of annotations and one sample
    that is split (tumor-normal case).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_small/s_small.txt")
    return open(path, "rt")


@pytest.fixture
def small_assay_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small/a_small.txt")
    return open(path, "rt")


@pytest.fixture
def full_investigation_file():
    """This file contains values for each normal investigation section and key.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_fullinvest/i_fullinvest.txt")
    return open(path, "rt")


@pytest.fixture
def full2_investigation_file():
    """This file contains values for each normal investigation section and key.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_fullinvest2/i_fullinvest2.txt")
    return open(path, "rt")


@pytest.fixture
def comment_investigation_file():
    """This file contains comments for each investigation section.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_comments/i_comments.txt")
    return open(path, "rt")


@pytest.fixture
def assays_investigation_file():
    """This file contains two studies with no assays, once with
    tab-separation (empty column) and once without (no column).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_assays/i_assays.txt")
    return open(path, "rt")


@pytest.fixture
def assays2_investigation_file():
    """This file contains two studies with no assays, once with
    tab-separation (empty column) and once without (no column).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_assays2/i_assays2.txt")
    return open(path, "rt")


@pytest.fixture
def small2_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small2/i_small2.txt")
    return open(path, "rt")


@pytest.fixture
def small2_study_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small2/s_small2.txt")
    return open(path, "rt")


@pytest.fixture
def small2_assay_file():
    """This file contains splitting and pooling examples.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_small2/a_small2.txt")
    return open(path, "rt")


@pytest.fixture
def gelelect_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/test_gelelect/i_Investigation.txt")
    return open(path, "rt")


@pytest.fixture
def gelelect_assay_file():
    """This file contains special cases for gel electrophoresis assays.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        "data/test_gelelect/a_study01_protein_expression_profiling_gel_electrophoresis.txt",
    )
    return open(path, "rt")


@pytest.fixture
def BII_I_1_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/BII-I-1/i_investigation.txt")
    return open(path, "rt")


@pytest.fixture
def BII_I_2_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/BII-I-2/i_investigation.txt")
    return open(path, "rt")

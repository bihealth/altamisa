# -*- coding: utf-8 -*-
"""Shared code for the tests.
"""

import os.path
import pytest


@pytest.fixture
def minimal_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/i_minimal.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def minimal2_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal2/i_minimal2.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def minimal_study_file():
    """This file only contains the bare essentials, although ISA-Tab might
    actually forgive us having no ``Process``.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/s_minimal.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def minimal_assay_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_minimal/a_minimal.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def small_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small/i_small.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def small_study_file():
    """This file contains a very limited number of annotations and one sample
    that is split (tumor-normal case).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_small/s_small.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def small_assay_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small/a_small.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def full_investigation_file():
    """This file contains values for each normal investigation section and key.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_fullinvest/i_fullinvest.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def full2_investigation_file():
    """This file contains values for each normal investigation section and key.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_fullinvest2/i_fullinvest2.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def comment_investigation_file():
    """This file contains comments for each investigation section.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_comments/i_comments.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assays_investigation_file():
    """This file contains two studies with no assays, once with
    tab-separation (empty column) and once without (no column).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_assays/i_assays.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assays2_investigation_file():
    """This file contains two studies with no assays, once with
    tab-separation (empty column) and once without (no column).
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_assays2/i_assays2.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def small2_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small2/i_small2.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def small2_study_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_small2/s_small2.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def small2_assay_file():
    """This file contains splitting and pooling examples.
    """
    path = os.path.join(os.path.dirname(__file__), "data/i_small2/a_small2.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def gelelect_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/test_gelelect/i_Investigation.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def gelelect_assay_file():
    """This file contains special cases for gel electrophoresis assays.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        "data/test_gelelect/a_study01_protein_expression_profiling_gel_electrophoresis.txt",
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def BII_I_1_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/BII-I-1/i_investigation.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def BII_I_2_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/BII-I-2/i_investigation.txt")
    with open(path, "rt") as file:
        yield file


# File fixtures for testing exceptions -------------------------------------------------------------


@pytest.fixture
def assay_file_exception_labeled_header_format():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/a_exception_labeled_header_format.txt"
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_labeled_header_not_allowed():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/a_exception_labeled_header_not_allowed.txt"
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_duplicated_header():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/a_exception_duplicated_header.txt"
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_simple_header_not_allowed():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/a_exception_simple_header_not_allowed.txt"
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_term_source_ref_next_column():
    path = os.path.join(
        os.path.dirname(__file__),
        "data/test_exceptions/a_exception_term_source_ref_next_column.txt",
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_term_source_ref_stop_iteration():
    path = os.path.join(
        os.path.dirname(__file__),
        "data/test_exceptions/a_exception_term_source_ref_stop_iteration.txt",
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_unknown_header():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/a_exception_unknown_header.txt"
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def assay_file_exception_invalid_column_type():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/a_exception_invalid_column_type.txt"
    )
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def only_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_onlyinvest/i_onlyinvest.txt")
    with open(path, "rt") as file:
        yield file


@pytest.fixture
def investigation_file_exception_comment_format():
    path = os.path.join(
        os.path.dirname(__file__), "data/test_exceptions/i_invest_comment_format.txt"
    )
    with open(path, "rt") as file:
        yield file


# File fixtures for testing warnings ---------------------------------------------------------------


@pytest.fixture
def warnings_investigation_file():
    path = os.path.join(os.path.dirname(__file__), "data/i_warnings/i_warnings.txt")
    with open(path, "rt") as file:
        yield file

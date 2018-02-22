# -*- coding: utf-8 -*-
"""Tests for parsing ISA investigation files"""

import pytest


from altamisa.isatab import InvestigationReader


def test_parse_minimal_investigation(minimal_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(minimal_investigation_file)
    investigation = reader.read()

    # Check results
    # Investigation
    assert investigation
    # assert "Minimal Investigation" == investigation.info.title
    # assert "i_minimal" == investigation.info.identifier
    #
    # # Studies
    # assert len(investigation.studies) == 1
    # assert "s_minimal" == investigation.studies[0].info.identifier
    # assert "Minimal Germline Study" == investigation.studies[0].info.title
    # assert "s_minimal.txt" == investigation.studies[0].info.path
    #
    # # Assays
    # assert len(investigation.studies) == 1
    # assert "s_minimal" == investigation.studies[0].info.identifier
    # assert "Minimal Germline Study" == investigation.studies[0].info.title
    # assert "s_minimal.txt" == investigation.studies[0].info.path

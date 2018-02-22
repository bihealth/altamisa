# -*- coding: utf-8 -*-
"""Tests for parsing ISA files"""

from io import StringIO

import pytest


from altamisa.isatab import InvestigationReader


def test_parse_minimal_investigation(minimal_investigation_txt):
    # Prepare file-like object
    investigation_io = StringIO(minimal_investigation_txt)
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(investigation_io)
    investigation = reader.read()
    # Check results
    assert investigation

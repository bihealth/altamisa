# -*- coding: utf-8 -*-
"""Tests for parsing ISA investigation files"""

import pytest


from altamisa.isatab import models
from altamisa.isatab import InvestigationReader


def test_parse_minimal_investigation(minimal_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(minimal_investigation_file)
    investigation = reader.read()

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 1 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        'OBI', 'http://data.bioontology.org/ontologies/OBI',
        '31', 'Ontology for Biomedical Investigations')
    assert expected == investigation.ontology_source_refs['OBI']

    # Basic info
    assert "Minimal Investigation" == investigation.info.title
    assert "i_minimal" == investigation.info.identifier

    # Studies
    assert len(investigation.studies) == 1
    assert "s_minimal" == investigation.studies[0].info.identifier
    assert "Minimal Germline Study" == investigation.studies[0].info.title
    assert "s_minimal.txt" == investigation.studies[0].info.path

    # Assays
    assert len(investigation.studies[0].assays) == 1
    assay = investigation.studies[0].assays["a_minimal.txt"]
    assert "a_minimal.txt" == assay.path

def test_parse_small_investigation(small_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(small_investigation_file)
    investigation = reader.read()

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 2 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        'OBI', 'http://data.bioontology.org/ontologies/OBI',
        '31', 'Ontology for Biomedical Investigations')
    assert expected == investigation.ontology_source_refs['OBI']
    expected = models.OntologyRef(
        'NCBITAXON', 'http://data.bioontology.org/ontologies/NCBITAXON', '8',
        ('National Center for Biotechnology Information (NCBI) Organismal '
         'Classification'))
    assert expected == investigation.ontology_source_refs['NCBITAXON']

    # Basic info
    assert "Small Investigation" == investigation.info.title
    assert "i_small" == investigation.info.identifier

    # Studies
    assert len(investigation.studies) == 1
    assert "s_small" == investigation.studies[0].info.identifier
    assert "Small Germline Study" == investigation.studies[0].info.title
    assert "s_small.txt" == investigation.studies[0].info.path

    # Assays
    assert len(investigation.studies[0].assays) == 1
    assay = investigation.studies[0].assays["a_small.txt"]
    assert "a_small.txt" == assay.path

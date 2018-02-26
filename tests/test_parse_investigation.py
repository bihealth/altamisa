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

def test_parse_full_investigation(full_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(full_investigation_file)
    investigation = reader.read()

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 9 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        'OBI', 'http://data.bioontology.org/ontologies/OBI',
        '21', 'Ontology for Biomedical Investigations')
    assert expected == investigation.ontology_source_refs['OBI']
    expected = models.OntologyRef(
        'NCBITAXON', 'http://data.bioontology.org/ontologies/NCBITAXON', '2',
        ('National Center for Biotechnology Information (NCBI) Organismal '
         'Classification'))
    assert expected == investigation.ontology_source_refs['NCBITAXON']

    # Basic info
    assert ("Growth control of the eukaryote cell: a systems biology study "
            "in yeast") == investigation.info.title
    assert "BII-I-1" == investigation.info.identifier
    assert "2007-04-30" == investigation.info.submission_date
    assert "2009-03-10" == investigation.info.public_release_date

    # Publications
    assert 3 == len(investigation.publications)
    expected = models.PublicationInfo(
        "17439666", "doi:10.1186/jbiol54",
        "Castrillo JI, Zeef LA, Hoyle DC, Zhang N, Hayes A, Gardner DC, "
        "Cornell MJ, Petty J, Hakes L, Wardleworth L, Rash B, Brown M, "
        "Dunn WB, Broadhurst D, O'Donoghue K, Hester SS, Dunkley TP, Hart "
        "SR, Swainston N, Li P, Gaskell SJ, Paton NW, Lilley KS, Kell DB, "
        "Oliver SG.",
        "Growth control of the eukaryote cell: a systems biology study in "
        "yeast.", models.OntologyTermRef("indexed in Pubmed", "", ""))
    assert expected == investigation.publications[0]
    expected = models.PublicationInfo(
        "1231222", "",
        "Piatnochka IT.",
        "Effect of prednisolone on the cardiovascular system in complex "
        "treatment of newly detected pulmonary tuberculosis",
        models.OntologyTermRef("published",
                               "http://www.ebi.ac.uk/efo/EFO_0001796", "EFO"))
    assert expected == investigation.publications[1]

    # Studies
    assert len(investigation.studies) == 2
    assert "BII-S-1" == investigation.studies[0].info.identifier
    assert ("Study of the impact of changes in flux on the transcriptome, "
            "proteome, endometabolome and exometabolome of the yeast "
            "Saccharomyces cerevisiae under different nutrient limitations"
            ) == investigation.studies[0].info.title
    assert "s_BII-S-1.txt" == investigation.studies[0].info.path

    # Assays
    assert len(investigation.studies[0].assays) == 3
    assay = investigation.studies[0].assays["a_proteome.txt"]
    assert "a_proteome.txt" == assay.path

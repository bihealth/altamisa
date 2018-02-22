# -*- coding: utf-8 -*-
"""Shared code for the tests.
"""

import textwrap

import pytest


@pytest.fixture
def minimal_investigation_txt():
    return textwrap.dedent("""
        ONTOLOGY SOURCE REFERENCE
        Term Source Name\t"NCBITAXON"\t"OBI"
        Term Source File\t"http://data.bioontology.org/ontologies/NCBITAXON"\t"http://data.bioontology.org/ontologies/OBI"
        Term Source Version\t"2"\t"21"
        Term Source Description\t"National Center for Biotechnology Information (NCBI) Organismal Classification"\t"Ontology for Biomedical Investigations"
        INVESTIGATION
        Investigation Identifier
        Investigation Title
        Investigation Description
        Investigation Submission Date
        Investigation Public Release Date
        INVESTIGATION PUBLICATIONS
        Investigation PubMed ID
        Investigation Publication DOI
        Investigation Publication Author List
        Investigation Publication Title
        Investigation Publication Status
        Investigation Publication Status Term Accession Number
        Investigation Publication Status Term Source REF
        INVESTIGATION CONTACTS
        Investigation Person Last Name
        Investigation Person First Name
        Investigation Person Mid Initials
        Investigation Person Email
        Investigation Person Phone
        Investigation Person Fax
        Investigation Person Address
        Investigation Person Affiliation
        Investigation Person Roles
        Investigation Person Roles Term Accession Number
        Investigation Person Roles Term Source REF
        STUDY
        Study Identifier\t"s_minimal"
        Study Title\t"Minimal Study"
        Study Description\t""
        Study Submission Date\t"2007-04-30"
        Study Public Release Date\t"2009-03-10"
        Study File Name\t"s_minimal.txt"
        STUDY DESIGN DESCRIPTORS
        Study Design Type\t"minimal design"
        Study Design Type Term Accession Number\t""
        Study Design Type Term Source REF\t""
        STUDY PUBLICATIONS
        Study PubMed ID
        Study Publication DOI
        Study Publication Author List
        Study Publication Title
        Study Publication Status
        Study Publication Status Term Accession Number
        Study Publication Status Term Source REF
        STUDY FACTORS
        Study Factor Name\t"first factor"
        Study Factor Type\t"chemical entity"
        Study Factor Type Term Accession Number\t"http://purl.obolibrary.org/obo/CHEBI_24431"
        Study Factor Type Term Source REF\t"CHEBI"
        STUDY ASSAYS
        Study Assay File Name\t"a_minimal.txt"
        Study Assay Measurement Type\t"protein expression profiling"
        Study Assay Measurement Type Term Accession Number\t"http://purl.obolibrary.org/obo/OBI_0000615"
        Study Assay Measurement Type Term Source REF\t"OBI"
        Study Assay Technology Type\t"mass spectrometry"
        Study Assay Technology Type Term Accession Number\t"http://purl.obolibrary.org/obo/OBI_0000470"
        Study Assay Technology Type Term Source REF\t"OBI"
        Study Assay Technology Platform\t"iTRAQ"
        STUDY PROTOCOLS
        Study Protocol Name\t"growth protocol"\t"mRNA extraction"\t"protein extraction"\t"biotin labeling"\t"ITRAQ labeling"\t"EukGE-WS4"\t"metabolite extraction"
        Study Protocol Type\t"growth"\t"RNA extraction"\t"extraction"\t"addition of molecular label"\t"addition of molecular label"\t"nucleic acid hybridization"\t"extraction"
        Study Protocol Type Term Accession Number\t""\t"http://purl.obolibrary.org/obo/OBI_0666666"\t"http://purl.obolibrary.org/obo/OBI_0302884"\t"http://purl.obolibrary.org/obo/OBI_0600038"\t"http://purl.obolibrary.org/obo/OBI_0600038"\t"http://purl.obolibrary.org/obo/OBI_0302903"\t"http://purl.obolibrary.org/obo/OBI_0302884"
        Study Protocol Type Term Source REF\t""\t"OBI"\t"OBI"\t"OBI"\t"OBI"\t"OBI"\t"OBI"
        Study Protocol Description\t""\t""\t""\t""\t""\t""\t""
        Study Protocol URI\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Version\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Parameters Name\t""\t""\t""\t""\t""\t""\t"standard volume;sample volume"
        Study Protocol Parameters Name Term Accession Number\t""\t""\t""\t""\t""\t""\t";"
        Study Protocol Parameters Name Term Source REF\t""\t""\t""\t""\t""\t""\t";"
        Study Protocol Components Name\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Type\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Type Term Accession Number\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Type Term Source REF\t""\t""\t""\t""\t""\t""\t""
        STUDY CONTACTS
        Study Person Last Name
        Study Person First Name
        Study Person Mid Initials
        Study Person Email
        Study Person Phone
        Study Person Fax
        Study Person Address
        Study Person Affiliation
        Study Person Roles Term Accession Number
        Study Person Roles Term Source REF
        STUDY
        Study Identifier\t"s_minimal"
        Study Title\t"Minimal Study"
        Study Description\t""
        Study Submission Date\t"2007-04-30"
        Study Public Release Date\t"2009-03-10"
        Study File Name\t"s_minimal.txt"
        STUDY DESIGN DESCRIPTORS
        Study Design Type\t"time series design"
        Study Design Type Term Accession Number\t"http://purl.obolibrary.org/obo/OBI_0500020"
        Study Design Type Term Source REF\t"OBI"
        STUDY PUBLICATIONS
        Study PubMed ID\t"17439666"
        Study Publication DOI\t""
        Study Publication Author List\t""
        Study Publication Title\t"Growth control of the eukaryote cell: a systems biology study in yeast."
        Study Publication Status\t"indexed in Pubmed"
        Study Publication Status Term Accession Number\t""
        Study Publication Status Term Source REF\t""
        STUDY FACTORS
        Study Factor Name\t"compound"\t"exposure time"\t"dose"
        Study Factor Type\t"chemical entity"\t"time"\t"dose"
        Study Factor Type Term Accession Number\t"http://purl.obolibrary.org/obo/CHEBI_24431"\t"http://purl.obolibrary.org/obo/PATO_0000165"\t"http://purl.obolibrary.org/obo/OBI_0000984"
        Study Factor Type Term Source REF\t"CHEBI"\t"OBI_BCGO"\t"OBI"
        STUDY ASSAYS
        Study Assay File Name\t"a_microarray.txt"
        Study Assay Measurement Type\t"transcription profiling"
        Study Assay Measurement Type Term Accession Number\t"http://purl.obolibrary.org/obo/OBI_0000424"
        Study Assay Measurement Type Term Source REF\t"OBI"
        Study Assay Technology Type\t"DNA microarray"
        Study Assay Technology Type Term Accession Number\t"http://purl.obolibrary.org/obo/OBI_0400148"
        Study Assay Technology Type Term Source REF\t"OBI"
        Study Assay Technology Platform\t"Affymetrix"
        STUDY PROTOCOLS
        Study Protocol Name\t"EukGE-WS4"\t"mRNA extraction"\t"biotin labeling"\t"extraction"\t"labeling"\t"NMR spectroscopy"\t"nmr assay"\t"data normalization"\t"data transformation"\t"sample collection"
        Study Protocol Type\t"nucleic acid hybridization"\t"RNA extraction"\t"addition of molecular label"\t"extraction"\t"addition of molecular label"\t"NMR spectroscopy"\t"nmr assay"\t"normalization data transformation"\t"data transformation"\t"sample collection"
        Study Protocol Type Term Accession Number\t"http://purl.obolibrary.org/obo/OBI_0302903"\t"http://purl.obolibrary.org/obo/OBI_0666666"\t"http://purl.obolibrary.org/obo/OBI_0600038"\t"http://purl.obolibrary.org/obo/OBI_0302884"\t"http://purl.obolibrary.org/obo/OBI_0600038"\t"http://purl.obolibrary.org/obo/OBI_0000623"\t""\t"http://purl.obolibrary.org/obo/OBI_0200169"\t"http://purl.obolibrary.org/obo/OBI_0200000"\t""
        Study Protocol Type Term Source REF\t"OBI"\t"OBI"\t"OBI"\t"OBI"\t"OBI"\t"OBI"\t""\t"OBI"\t"OBI"\t""
        Study Protocol Description\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol URI\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Version\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Parameters Name\t""\t""\t""\t""\t""\t";;;"\t""\t""\t""\t""
        Study Protocol Parameters Name Term Accession Number\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Parameters Name Term Source REF\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Name\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Type\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Type Term Accession Number\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        Study Protocol Components Type Term Source REF\t""\t""\t""\t""\t""\t""\t""\t""\t""\t""
        STUDY CONTACTS
        Study Person Last Name
        Study Person First Name
        Study Person Mid Initials
        Study Person Email
        Study Person Phone
        Study Person Fax
        Study Person Address
        Study Person Affiliation
        Study Person Roles
        Study Person Roles Term Accession Number
        Study Person Roles Term Source REF
        Comment[Study Person REF]\t""\t""\t""
        """.rstrip())

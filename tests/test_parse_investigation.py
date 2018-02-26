# -*- coding: utf-8 -*-
"""Tests for parsing ISA investigation files"""

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

    # Contacts
    assert 3 == len(investigation.contacts)
    expected = models.ContactInfo(
        "Oliver", "Stephen", "G", "stephen.oliver@test.mail", "", "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, "
        "University of Manchester",
        models.OntologyTermRef("corresponding author", "", ""))
    assert expected == investigation.contacts[0]
    expected = models.ContactInfo(
        "Juan", "Castrillo", "I", "", "123456789", "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, "
        "University of Manchester",
        models.OntologyTermRef("author", "", ""))
    assert expected == investigation.contacts[1]
    expected = models.ContactInfo(
        "Leo", "Zeef", "A", "", "", "+49 123456789",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, "
        "University of Manchester",
        models.OntologyTermRef("author",
                               "http://purl.obolibrary.org/obo/RoleO_0000061",
                               "ROLEO"))
    assert expected == investigation.contacts[2]

    # Studies
    assert len(investigation.studies) == 2

    # Study 1
    study = investigation.studies[0]
    assert "BII-S-1" == study.info.identifier
    assert ("Study of the impact of changes in flux on the transcriptome, "
            "proteome, endometabolome and exometabolome of the yeast "
            "Saccharomyces cerevisiae under different nutrient limitations"
            ) == study.info.title
    assert "s_BII-S-1.txt" == study.info.path

    # Study 1 - Design descriptors
    assert 2 == len(study.designs)
    expected = (models.OntologyTermRef(
                    "intervention design",
                    "http://purl.obolibrary.org/obo/OBI_0000115",
                    "OBI"),
                models.OntologyTermRef(
                    "genotyping design",
                    "http://purl.obolibrary.org/obo/OBI_0001444",
                    "OBI"))
    assert expected == study.designs

    # Study 1 - Publications
    assert 1 == len(study.publications)
    expected = models.PublicationInfo(
        "17439666", "doi:10.1186/jbiol54",
        "Castrillo JI, Zeef LA, Hoyle DC, Zhang N, Hayes A, Gardner DC, "
        "Cornell MJ, Petty J, Hakes L, Wardleworth L, Rash B, Brown M, "
        "Dunn WB, Broadhurst D, O'Donoghue K, Hester SS, Dunkley TP, Hart "
        "SR, Swainston N, Li P, Gaskell SJ, Paton NW, Lilley KS, Kell DB, "
        "Oliver SG.",
        "Growth control of the eukaryote cell: a systems biology study in "
        "yeast.", models.OntologyTermRef("published", "", ""))
    assert expected == study.publications[0]

    # Study 1 - Factors
    assert 2 == len(study.factors)
    expected = models.FactorInfo(
        "limiting nutrient", models.OntologyTermRef(
                    "chemical entity",
                    "http://purl.obolibrary.org/obo/CHEBI_24431",
                    "CHEBI"))
    assert expected == study.factors["limiting nutrient"]
    expected = models.FactorInfo(
        "rate", models.OntologyTermRef(
            "rate",
            "http://purl.obolibrary.org/obo/PATO_0000161",
            "PATO"))
    assert expected == study.factors["rate"]

    # Study 1 - Assays
    assert 3 == len(study.assays)
    assay = study.assays["a_proteome.txt"]
    assert "a_proteome.txt" == assay.path

    # Study 1 - Protocols
    assert 7 == len(study.protocols)
    expected = models.ProtocolInfo(
        "growth protocol", models.OntologyTermRef("growth", "", ""),
        "1. Biomass samples (45 ml) were taken via the sample port of the "
        "Applikon fermenters. The cells were pelleted by centrifugation for 5 "
        "min at 5000 rpm. The supernatant was removed and the RNA pellet "
        "resuspended in the residual medium to form a slurry. This was added "
        "in a dropwise manner directly into a 5 ml Teflon flask (B. Braun "
        "Biotech, Germany) containing liquid nitrogen and a 7 mm-diameter "
        "tungsten carbide ball. After allowing evaporation of the liquid "
        "nitrogen the flask was reassembled and the cells disrupted by "
        "agitation at 1500 rpm for 2 min in a Microdismembranator U (B. Braun "
        "Biotech, Germany) 2. The frozen powder was then dissolved in 1 ml of "
        "TriZol reagent (Sigma-Aldrich, UK), vortexed for 1 min, and then kept"
        " at room temperature for a further 5min. 3. Chloroform extraction was"
        " performed by addition of 0.2 ml chloroform, shaking vigorously or 15"
        " s, then 5min incubation at room temperature. 4. Following "
        "centrifugation at 12,000 rpm for 5 min, the RNA (contained in the "
        "aqueous phase) was precipitated with 0.5 vol of 2-propanol at room "
        "temperature for 15 min. 5. After further centrifugation (12,000 rpm "
        "for 10 min at 4 C) the RNA pellet was washed twice with 70 % (v/v) "
        "ethanol, briefly air-dried, and redissolved in 0.5 ml diethyl "
        "pyrocarbonate (DEPC)-treated water. 6. The single-stranded RNA was "
        "precipitated once more by addition of 0.5 ml of LiCl buffer (4 M "
        "LiCl, 20 mM Tris-HCl, pH 7.5, 10 mM EDTA), thus removing tRNA and "
        "DNA from the sample. 7. After precipitation (20 C for 1h) and "
        "centrifugation (12,000 rpm, 30 min, 4 C), the RNA was washed twice in"
        " 70 % (v/v) ethanol prior to being dissolved in a minimal volume of "
        "DEPC-treated water. 8. Total RNA quality was checked using the RNA "
        "6000 Nano Assay, and analysed on an Agilent 2100 Bioanalyser (Agilent"
        " Technologies). RNA was quantified using the Nanodrop ultra low "
        "volume spectrophotometer (Nanodrop Technologies).",
        "", "",
        models.OntologyTermRef(
            "rate", "http://purl.obolibrary.org/obo/PATO_0000161", "PATO"),
        models.ProtocolComponentInfo("", models.OntologyTermRef("", "", "")))
    assert expected == study.protocols["growth protocol"]
    expected = models.ProtocolInfo(
        "metabolite extraction",
        models.OntologyTermRef(
            "extraction", "http://purl.obolibrary.org/obo/OBI_0302884", "OBI"),
        "",  "", "",
        models.OntologyTermRef(
            "standard volume;sample volume", ";", ";"),
        models.ProtocolComponentInfo(
            "pipette", models.OntologyTermRef(
                "instrument", "http://www.ebi.ac.uk/efo/EFO_0000548", "EFO")))
    assert expected == study.protocols["metabolite extraction"]

    # Study 1 - Contacts
    assert 3 == len(study.contacts)
    expected = models.ContactInfo(
        "Oliver", "Stephen", "G", "stephen.oliver@test.mail", "", "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, "
        "University of Manchester",
        models.OntologyTermRef("corresponding author", "", ""))
    assert expected == study.contacts[0]
    expected = models.ContactInfo(
        "Juan", "Castrillo", "I", "", "123456789", "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, "
        "University of Manchester",
        models.OntologyTermRef("author",
                               "http://purl.obolibrary.org/obo/RoleO_0000061",
                               "ROLEO"))
    assert expected == study.contacts[1]
    expected = models.ContactInfo(
        "Leo", "Zeef", "A", "", "", "+49 123456789",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, "
        "University of Manchester",
        models.OntologyTermRef("author",
                               "http://purl.obolibrary.org/obo/RoleO_0000061",
                               "ROLEO"))
    assert expected == study.contacts[2]

    # Study 2
    study = investigation.studies[1]
    expected = models.BasicInfo(
        "s_BII-S-2.txt", "BII-S-2",
        "A time course analysis of transcription response in yeast treated "
        "with rapamycin, a specific inhibitor of the TORC1 complex: impact "
        "on yeast growth",
        "Comprehensive high-throughput analyses at the levels of mRNAs, "
        "proteins, and metabolites, and studies on gene expression patterns "
        "are required for systems biology studies of cell growth [4,26-29]. "
        "Although such comprehensive data sets are lacking, many studies have "
        "pointed to a central role for the target-of-rapamycin (TOR) signal "
        "transduction pathway in growth control. TOR is a serine/threonine "
        "kinase that has been conserved from yeasts to mammals; it integrates "
        "signals from nutrients or growth factors to regulate cell growth and "
        "cell-cycle progression coordinately. Although such comprehensive data "
        "sets are lacking, many studies have pointed to a central role for the "
        "target-of-rapamycin (TOR) signal transduction pathway in growth "
        "control. TOR is a serine/threonine kinase that has been conserved "
        "from yeasts to mammals; it integrates signals from nutrients or "
        "growth factors to regulate cell growth and cell-cycle progression "
        "coordinately. The effect of rapamycin were studied as follows: a "
        "culture growing at mid-exponential phase was divided into two. "
        "Rapamycin (200 ng/ml) was added to one half, and the drug's solvent "
        "to the other, as the control. Samples were taken at 0, 1, 2 and 4 h "
        "after treatment. Gene expression at the mRNA level was investigated "
        "by transcriptome analysis using Affymetrix hybridization arrays.",
        "2007-04-30", "2009-03-10")
    assert expected == study.info

# -*- coding: utf-8 -*-
"""Tests for parsing ISA investigation files"""


from datetime import date
from pathlib import Path
import pytest
import warnings


from altamisa.constants import investigation_headers
from altamisa.exceptions import (
    AdvisoryIsaValidationWarning,
    CriticalIsaValidationWarning,
    IsaWarning,
    ModerateIsaValidationWarning,
    ParseIsatabWarning,
)
from altamisa.isatab import models
from altamisa.isatab import InvestigationReader, InvestigationValidator


def test_parse_minimal_investigation(minimal_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(minimal_investigation_file)
    investigation = reader.read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 2 == len(record)

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 1 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        "OBI",
        "http://data.bioontology.org/ontologies/OBI",
        "31",
        "Ontology for Biomedical Investigations",
        (),
        [*investigation_headers.ONTOLOGY_SOURCE_REF_KEYS],
    )
    assert expected == investigation.ontology_source_refs["OBI"]

    # Basic info
    assert "Minimal Investigation" == investigation.info.title
    assert "i_minimal" == investigation.info.identifier

    # Studies
    assert len(investigation.studies) == 1
    assert "s_minimal" == investigation.studies[0].info.identifier
    assert "Minimal Germline Study" == investigation.studies[0].info.title
    assert Path("s_minimal.txt") == investigation.studies[0].info.path

    # Assays
    assert len(investigation.studies[0].assays) == 1
    assay = investigation.studies[0].assays[0]
    assert Path("a_minimal.txt") == assay.path

    # Study contacts
    assert 0 == len(investigation.studies[0].contacts)


def test_parse_small_investigation(small_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(small_investigation_file)
    investigation = reader.read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 2 == len(record)

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 4 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        "OBI",
        "http://data.bioontology.org/ontologies/OBI",
        "31",
        "Ontology for Biomedical Investigations",
        (),
        [*investigation_headers.ONTOLOGY_SOURCE_REF_KEYS],
    )
    assert expected == investigation.ontology_source_refs["OBI"]
    expected = models.OntologyRef(
        "NCBITAXON",
        "http://data.bioontology.org/ontologies/NCBITAXON",
        "8",
        ("National Center for Biotechnology Information (NCBI) Organismal " "Classification"),
        (),
        [*investigation_headers.ONTOLOGY_SOURCE_REF_KEYS],
    )
    assert expected == investigation.ontology_source_refs["NCBITAXON"]
    expected = models.OntologyRef(
        "ROLEO",
        "http://data.bioontology.org/ontologies/ROLEO",
        "1",
        "Role Ontology",
        (),
        [*investigation_headers.ONTOLOGY_SOURCE_REF_KEYS],
    )
    assert expected == investigation.ontology_source_refs["ROLEO"]

    # Basic info
    assert "Small Investigation" == investigation.info.title
    assert "i_small" == investigation.info.identifier

    # Studies
    assert len(investigation.studies) == 1
    assert "s_small" == investigation.studies[0].info.identifier
    assert "Small Germline Study" == investigation.studies[0].info.title
    assert Path("s_small.txt") == investigation.studies[0].info.path

    # Assays
    assert len(investigation.studies[0].assays) == 1
    assay = investigation.studies[0].assays[0]
    assert Path("a_small.txt") == assay.path

    # Study contacts
    assert 1 == len(investigation.studies[0].contacts)


def test_parse_full_investigation(full_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(full_investigation_file)
    investigation = reader.read()
    InvestigationValidator(investigation).validate()

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 9 == len(investigation.ontology_source_refs)
    expected_headers = [*investigation_headers.ONTOLOGY_SOURCE_REF_KEYS, "Comment[Test]"]
    expected = models.OntologyRef(
        "OBI",
        "http://data.bioontology.org/ontologies/OBI",
        "21",
        "Ontology for Biomedical Investigations",
        (models.Comment("Test", "4"),),
        expected_headers,
    )
    assert expected == investigation.ontology_source_refs["OBI"]
    expected = models.OntologyRef(
        "NCBITAXON",
        "http://data.bioontology.org/ontologies/NCBITAXON",
        "2",
        ("National Center for Biotechnology Information (NCBI) Organismal " "Classification"),
        (models.Comment("Test", "1"),),
        expected_headers,
    )
    assert expected == investigation.ontology_source_refs["NCBITAXON"]

    # Basic info
    assert (
        "Growth control of the eukaryote cell: a systems biology study " "in yeast"
    ) == investigation.info.title
    assert "BII-I-1" == investigation.info.identifier
    assert date(2007, 4, 30) == investigation.info.submission_date
    assert date(2009, 3, 10) == investigation.info.public_release_date

    expected_headers = [
        *investigation_headers.INVESTIGATION_INFO_KEYS,
        "Comment[Created With Configuration]",
        "Comment[Last Opened With Configuration]",
        "Comment[Owning Organisation URI]",
        "Comment[Consortium URI]",
        "Comment[Principal Investigator URI]",
        "Comment[Investigation Keywords]",
    ]
    assert expected_headers == investigation.info.headers

    # Publications
    assert 3 == len(investigation.publications)
    expected_headers = [
        *investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS[0:4],
        "Comment[Subtitle]",
        *investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS[4:],
    ]
    expected = models.PublicationInfo(
        "17439666",
        "doi:10.1186/jbiol54",
        "Castrillo JI, Zeef LA, Hoyle DC, Zhang N, Hayes A, Gardner DC, "
        "Cornell MJ, Petty J, Hakes L, Wardleworth L, Rash B, Brown M, "
        "Dunn WB, Broadhurst D, O'Donoghue K, Hester SS, Dunkley TP, Hart "
        "SR, Swainston N, Li P, Gaskell SJ, Paton NW, Lilley KS, Kell DB, "
        "Oliver SG.",
        "Growth control of the eukaryote cell: a systems biology study in " "yeast.",
        models.OntologyTermRef("indexed in Pubmed", "", ""),
        (models.Comment("Subtitle", ""),),
        expected_headers,
    )
    assert expected == investigation.publications[0]
    expected = models.PublicationInfo(
        "1231222",
        "",
        "Piatnochka IT.",
        "Effect of prednisolone on the cardiovascular system in complex "
        "treatment of newly detected pulmonary tuberculosis",
        models.OntologyTermRef("published", "http://www.ebi.ac.uk/efo/EFO_0001796", "EFO"),
        (models.Comment("Subtitle", "Something"),),
        expected_headers,
    )
    assert expected == investigation.publications[1]

    # Contacts
    assert 3 == len(investigation.contacts)
    expected_headers = [
        *investigation_headers.INVESTIGATION_CONTACTS_KEYS,
        "Comment[Investigation Person ORCID]",
        "Comment[Investigation Person REF]",
    ]
    expected = models.ContactInfo(
        "Oliver",
        "Stephen",
        "G",
        "stephen.oliver@test.mail",
        "",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("corresponding author", "", ""),
        (
            models.Comment("Investigation Person ORCID", "12345"),
            models.Comment("Investigation Person REF", "personA"),
        ),
        expected_headers,
    )
    assert expected == investigation.contacts[0]
    expected = models.ContactInfo(
        "Juan",
        "Castrillo",
        "I",
        "",
        "123456789",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "", ""),
        (
            models.Comment("Investigation Person ORCID", "0987654321"),
            models.Comment("Investigation Person REF", "personB"),
        ),
        expected_headers,
    )
    assert expected == investigation.contacts[1]
    expected = models.ContactInfo(
        "Leo",
        "Zeef",
        "A",
        "",
        "",
        "+49 123456789",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (
            models.Comment("Investigation Person ORCID", "1357908642"),
            models.Comment("Investigation Person REF", "personC"),
        ),
        expected_headers,
    )
    assert expected == investigation.contacts[2]

    # Studies
    assert len(investigation.studies) == 2

    # Study 1
    study = investigation.studies[0]
    assert "BII-S-1" == study.info.identifier
    assert (
        "Study of the impact of changes in flux on the transcriptome, "
        "proteome, endometabolome and exometabolome of the yeast "
        "Saccharomyces cerevisiae under different nutrient limitations"
    ) == study.info.title
    assert Path("s_BII-S-1.txt") == study.info.path

    # Study 1 - Design descriptors
    assert 2 == len(study.designs)
    expected_headers = [
        *investigation_headers.STUDY_DESIGN_DESCR_KEYS[0:1],
        "Comment[Test1]",
        *investigation_headers.STUDY_DESIGN_DESCR_KEYS[1:],
        "Comment[Test2]",
    ]
    expected = (
        models.DesignDescriptorsInfo(
            models.OntologyTermRef(
                "intervention design", "http://purl.obolibrary.org/obo/OBI_0000115", "OBI"
            ),
            (models.Comment("Test1", "1"), models.Comment("Test2", "3")),
            expected_headers,
        ),
        models.DesignDescriptorsInfo(
            models.OntologyTermRef(
                "genotyping design", "http://purl.obolibrary.org/obo/OBI_0001444", "OBI"
            ),
            (models.Comment("Test1", "2"), models.Comment("Test2", "4")),
            expected_headers,
        ),
    )
    assert expected == study.designs

    # Study 1 - Publications
    assert 1 == len(study.publications)
    expected = models.PublicationInfo(
        "17439666",
        "doi:10.1186/jbiol54",
        "Castrillo JI, Zeef LA, Hoyle DC, Zhang N, Hayes A, Gardner DC, "
        "Cornell MJ, Petty J, Hakes L, Wardleworth L, Rash B, Brown M, "
        "Dunn WB, Broadhurst D, O'Donoghue K, Hester SS, Dunkley TP, Hart "
        "SR, Swainston N, Li P, Gaskell SJ, Paton NW, Lilley KS, Kell DB, "
        "Oliver SG.",
        "Growth control of the eukaryote cell: a systems biology study in " "yeast.",
        models.OntologyTermRef("published", "", ""),
        (models.Comment("Subtitle", "Something"),),
        [
            *investigation_headers.STUDY_PUBLICATIONS_KEYS[0:4],
            "Comment[Subtitle]",
            *investigation_headers.STUDY_PUBLICATIONS_KEYS[4:],
        ],
    )
    assert expected == study.publications[0]

    # Study 1 - Factors
    assert 2 == len(study.factors)
    expected_headers = [*investigation_headers.STUDY_FACTORS_KEYS, "Comment[FactorsTest]"]
    expected = models.FactorInfo(
        "limiting nutrient",
        models.OntologyTermRef(
            "chemical entity", "http://purl.obolibrary.org/obo/CHEBI_24431", "CHEBI"
        ),
        (models.Comment("FactorsTest", "1"),),
        expected_headers,
    )
    assert expected == study.factors["limiting nutrient"]
    expected = models.FactorInfo(
        "rate",
        models.OntologyTermRef("rate", "http://purl.obolibrary.org/obo/PATO_0000161", "PATO"),
        (models.Comment("FactorsTest", "2"),),
        expected_headers,
    )
    assert expected == study.factors["rate"]

    # Study 1 - Assays
    assert 3 == len(study.assays)
    expected_headers = [*investigation_headers.STUDY_ASSAYS_KEYS, "Comment[Extra Info]"]
    expected = models.AssayInfo(
        models.OntologyTermRef(
            "protein expression profiling", "http://purl.obolibrary.org/obo/OBI_0000615", "OBI"
        ),
        models.OntologyTermRef(
            "mass spectrometry", "http://purl.obolibrary.org/obo/OBI_0000470", "OBI"
        ),
        "iTRAQ",
        Path("a_proteome.txt"),
        (models.Comment("Extra Info", "a"),),
        expected_headers,
    )
    assert expected == study.assays[0]
    expected = models.AssayInfo(
        models.OntologyTermRef(
            "transcription profiling", "http://purl.obolibrary.org/obo/OBI_0000424", "OBI"
        ),
        models.OntologyTermRef(
            "DNA microarray", "http://purl.obolibrary.org/obo/OBI_0400148", "OBI"
        ),
        "Affymetrix",
        Path("a_transcriptome.txt"),
        (models.Comment("Extra Info", "c"),),
        expected_headers,
    )
    assert expected == study.assays[2]

    # Study 1 - Protocols
    assert 7 == len(study.protocols)
    expected_headers = [
        *investigation_headers.STUDY_PROTOCOLS_KEYS[0:7],
        "Comment[Protocol Rating]",
        *investigation_headers.STUDY_PROTOCOLS_KEYS[7:],
    ]
    expected = models.ProtocolInfo(
        "growth protocol",
        models.OntologyTermRef("growth", "", ""),
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
        "",
        "",
        {
            "rate": models.OntologyTermRef(
                "rate", "http://purl.obolibrary.org/obo/PATO_0000161", "PATO"
            )
        },
        {},
        (models.Comment("Protocol Rating", "1"),),
        expected_headers,
    )
    assert expected == study.protocols["growth protocol"]
    expected = models.ProtocolInfo(
        "metabolite extraction",
        models.OntologyTermRef("extraction", "http://purl.obolibrary.org/obo/OBI_0302884", "OBI"),
        "",
        "",
        "",
        {
            "standard volume": models.OntologyTermRef("standard volume", "", ""),
            "sample volume": models.OntologyTermRef("sample volume", "", ""),
        },
        {
            "pipette": models.ProtocolComponentInfo(
                "pipette",
                models.OntologyTermRef("instrument", "http://www.ebi.ac.uk/efo/EFO_0000548", "EFO"),
            )
        },
        (models.Comment("Protocol Rating", "7"),),
        expected_headers,
    )
    assert expected == study.protocols["metabolite extraction"]

    # Study 1 - Contacts
    assert 3 == len(study.contacts)
    expected_headers = [*investigation_headers.STUDY_CONTACTS_KEYS, "Comment[Study Person REF]"]
    expected = models.ContactInfo(
        "Oliver",
        "Stephen",
        "G",
        "stephen.oliver@test.mail",
        "",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("corresponding author", "", ""),
        (models.Comment("Study Person REF", ""),),
        expected_headers,
    )
    assert expected == study.contacts[0]
    expected = models.ContactInfo(
        "Juan",
        "Castrillo",
        "I",
        "",
        "123456789",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (models.Comment("Study Person REF", ""),),
        expected_headers,
    )
    assert expected == study.contacts[1]
    expected = models.ContactInfo(
        "Leo",
        "Zeef",
        "A",
        "",
        "",
        "+49 123456789",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (models.Comment("Study Person REF", ""),),
        expected_headers,
    )
    assert expected == study.contacts[2]

    # Study 2
    study = investigation.studies[1]
    expected = models.BasicInfo(
        Path("s_BII-S-2.txt"),
        "BII-S-2",
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
        date(2007, 4, 30),
        date(2009, 3, 10),
        (
            models.Comment("Study Grant Number", ""),
            models.Comment("Study Funding Agency", ""),
            models.Comment("Manuscript Licence", "CC BY 3.0"),
            models.Comment("Experimental Metadata Licence", "CC0"),
            models.Comment("Data Repository", ""),
            models.Comment("Data Record Accession", ""),
            models.Comment("Data Record URI", ""),
            models.Comment("Supplementary Information File Name", ""),
            models.Comment("Supplementary Information File Type", ""),
            models.Comment("Supplementary File URI", ""),
            models.Comment("Subject Keywords", ""),
        ),
        [
            *investigation_headers.STUDY_INFO_KEYS[0:3],
            "Comment[Study Grant Number]",
            "Comment[Study Funding Agency]",
            *investigation_headers.STUDY_INFO_KEYS[3:],
            "Comment[Manuscript Licence]",
            "Comment[Experimental Metadata Licence]",
            "Comment[Data Repository]",
            "Comment[Data Record Accession]",
            "Comment[Data Record URI]",
            "Comment[Supplementary Information File Name]",
            "Comment[Supplementary Information File Type]",
            "Comment[Supplementary File URI]",
            "Comment[Subject Keywords]",
        ],
    )
    assert expected == study.info

    # Study 2 - Factors
    assert 3 == len(study.factors)
    expected = models.FactorInfo(
        "exposure time",
        models.OntologyTermRef("time", "http://purl.obolibrary.org/obo/PATO_0000165", "OBI_BCGO"),
        (),
        [*investigation_headers.STUDY_FACTORS_KEYS],
    )
    assert expected == study.factors["exposure time"]

    # Study 2 - Assays
    assert 1 == len(study.assays)
    expected = models.AssayInfo(
        models.OntologyTermRef(
            "transcription profiling", "http://purl.obolibrary.org/obo/OBI_0000424", "OBI"
        ),
        models.OntologyTermRef(
            "DNA microarray", "http://purl.obolibrary.org/obo/OBI_0400148", "OBI"
        ),
        "Affymetrix",
        Path("a_microarray.txt"),
        (),
        [*investigation_headers.STUDY_ASSAYS_KEYS],
    )
    assert expected == study.assays[0]

    # Study 2 - Protocols
    assert 10 == len(study.protocols)
    expected = models.ProtocolInfo(
        "NMR spectroscopy",
        models.OntologyTermRef(
            "NMR spectroscopy", "http://purl.obolibrary.org/obo/OBI_0000623", "OBI"
        ),
        "",
        "",
        "",
        {},
        {
            "NMR tubes": models.ProtocolComponentInfo(
                "NMR tubes", models.OntologyTermRef(None, None, None)
            ),
            "Bruker-Av600": models.ProtocolComponentInfo(
                "Bruker-Av600",
                models.OntologyTermRef("instrument", "http://www.ebi.ac.uk/efo/EFO_0000548", "EFO"),
            ),
        },
        (),
        [*investigation_headers.STUDY_PROTOCOLS_KEYS],
    )
    assert expected == study.protocols["NMR spectroscopy"]

    # Study 2 - Contacts
    assert 3 == len(study.contacts)
    expected = models.ContactInfo(
        "Juan",
        "Castrillo",
        "I",
        "",
        "123456789",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (models.Comment("Study Person REF", "personB"),),
        [*investigation_headers.STUDY_CONTACTS_KEYS, "Comment[Study Person REF]"],
    )
    assert expected == study.contacts[1]


def test_parse_comment_investigation(comment_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(comment_investigation_file)
    investigation = reader.read()
    InvestigationValidator(investigation).validate()

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 9 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        "OBI",
        "http://data.bioontology.org/ontologies/OBI",
        "21",
        "Ontology for Biomedical Investigations",
        (models.Comment("OntologyComment", "TestValue01"),),
        [
            *investigation_headers.ONTOLOGY_SOURCE_REF_KEYS[0:2],
            "Comment[OntologyComment]",
            *investigation_headers.ONTOLOGY_SOURCE_REF_KEYS[2:],
        ],
    )
    assert expected == investigation.ontology_source_refs["OBI"]

    # Basic info
    assert "BII-I-1" == investigation.info.identifier
    assert "Owning Organisation URI" == investigation.info.comments[2].name
    assert "TestValue01" == investigation.info.comments[2].value

    expected_headers = [
        *investigation_headers.INVESTIGATION_INFO_KEYS,
        "Comment[Created With Configuration]",
        "Comment[Last Opened With Configuration]",
        "Comment[Owning Organisation URI]",
        "Comment[Consortium URI]",
        "Comment[Principal Investigator URI]",
        "Comment[Investigation Keywords]",
    ]

    # Publications
    assert 3 == len(investigation.publications)
    expected = models.PublicationInfo(
        "17439666",
        "doi:10.1186/jbiol54",
        "Castrillo JI, Zeef LA, Hoyle DC, Zhang N, Hayes A, Gardner DC, "
        "Cornell MJ, Petty J, Hakes L, Wardleworth L, Rash B, Brown M, "
        "Dunn WB, Broadhurst D, O'Donoghue K, Hester SS, Dunkley TP, Hart "
        "SR, Swainston N, Li P, Gaskell SJ, Paton NW, Lilley KS, Kell DB, "
        "Oliver SG.",
        "Growth control of the eukaryote cell: a systems biology study in " "yeast.",
        models.OntologyTermRef("indexed in Pubmed", "", ""),
        (models.Comment("InvestPubsComment", "TestValue01"),),
        [
            *investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS[0:2],
            "Comment[InvestPubsComment]",
            *investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS[2:],
        ],
    )
    assert expected == investigation.publications[0]

    # Contacts
    assert 3 == len(investigation.contacts)
    expected = models.ContactInfo(
        "Leo",
        "Zeef",
        "A",
        "",
        "",
        "+49 123456789",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (
            models.Comment("Investigation Person ORCID", "1357908642"),
            models.Comment("Investigation Person REF", "personC"),
        ),
        [
            *investigation_headers.INVESTIGATION_CONTACTS_KEYS,
            "Comment[Investigation Person ORCID]",
            "Comment[Investigation Person REF]",
        ],
    )
    assert expected == investigation.contacts[2]

    # Studies
    assert len(investigation.studies) == 2

    # Study 1
    study = investigation.studies[0]
    assert "BII-S-1" == study.info.identifier
    assert Path("s_BII-S-1.txt") == study.info.path
    assert "Manuscript Licence" == study.info.comments[2].name
    assert "CC BY 3.0" == study.info.comments[2].value

    expected_headers = [
        *investigation_headers.STUDY_INFO_KEYS[0:3],
        "Comment[Study Grant Number]",
        "Comment[Study Funding Agency]",
        *investigation_headers.STUDY_INFO_KEYS[3:],
        "Comment[Manuscript Licence]",
        "Comment[Experimental Metadata Licence]",
        "Comment[Data Repository]",
        "Comment[Data Record Accession]",
        "Comment[Data Record URI]",
        "Comment[Supplementary Information File Name]",
        "Comment[Supplementary Information File Type]",
        "Comment[Supplementary File URI]",
        "Comment[Subject Keywords]",
    ]
    assert expected_headers == study.info.headers

    # Study 1 - Design descriptors
    assert 2 == len(study.designs)
    expected = models.DesignDescriptorsInfo(
        models.OntologyTermRef(
            "genotyping design", "http://purl.obolibrary.org/obo/OBI_0001444", "OBI"
        ),
        (models.Comment("DesignDescsComment", "TestValue01"),),
        [*investigation_headers.STUDY_DESIGN_DESCR_KEYS, "Comment[DesignDescsComment]"],
    )
    assert expected == study.designs[1]

    # Study 1 - Publications
    assert 1 == len(study.publications)
    expected = models.PublicationInfo(
        "17439666",
        "doi:10.1186/jbiol54",
        "Castrillo JI, Zeef LA, Hoyle DC, Zhang N, Hayes A, Gardner DC, "
        "Cornell MJ, Petty J, Hakes L, Wardleworth L, Rash B, Brown M, "
        "Dunn WB, Broadhurst D, O'Donoghue K, Hester SS, Dunkley TP, Hart "
        "SR, Swainston N, Li P, Gaskell SJ, Paton NW, Lilley KS, Kell DB, "
        "Oliver SG.",
        "Growth control of the eukaryote cell: a systems biology study in " "yeast.",
        models.OntologyTermRef("published", "", ""),
        (models.Comment("StudyPubsComment", "TestValue01"),),
        [
            *investigation_headers.STUDY_PUBLICATIONS_KEYS[0:4],
            "Comment[StudyPubsComment]",
            *investigation_headers.STUDY_PUBLICATIONS_KEYS[4:],
        ],
    )
    assert expected == study.publications[0]

    # Study 1 - Factors
    assert 2 == len(study.factors)
    expected = models.FactorInfo(
        "rate",
        models.OntologyTermRef("rate", "http://purl.obolibrary.org/obo/PATO_0000161", "PATO"),
        (models.Comment("FactorsComment", "TestValue01"),),
        [*investigation_headers.STUDY_FACTORS_KEYS, "Comment[FactorsComment]"],
    )
    assert expected == study.factors["rate"]

    # Study 1 - Assays
    assert 3 == len(study.assays)
    expected = models.AssayInfo(
        models.OntologyTermRef(
            "transcription profiling", "http://purl.obolibrary.org/obo/OBI_0000424", "OBI"
        ),
        models.OntologyTermRef(
            "DNA microarray", "http://purl.obolibrary.org/obo/OBI_0400148", "OBI"
        ),
        "Affymetrix",
        Path("a_transcriptome.txt"),
        (models.Comment("AssaysComment", "A comment within ontology terms?"),),
        [
            *investigation_headers.STUDY_ASSAYS_KEYS[0:5],
            "Comment[AssaysComment]",
            *investigation_headers.STUDY_ASSAYS_KEYS[5:],
        ],
    )
    assert expected == study.assays[2]

    # Study 1 - Protocols
    assert 7 == len(study.protocols)
    expected = models.ProtocolInfo(
        "metabolite extraction",
        models.OntologyTermRef("extraction", "http://purl.obolibrary.org/obo/OBI_0302884", "OBI"),
        "",
        "",
        "",
        {
            "standard volume": models.OntologyTermRef("standard volume", "", ""),
            "sample volume": models.OntologyTermRef("sample volume", "", ""),
        },
        {
            "pipette": models.ProtocolComponentInfo(
                "pipette",
                models.OntologyTermRef("instrument", "http://www.ebi.ac.uk/efo/EFO_0000548", "EFO"),
            )
        },
        (models.Comment("ProtocolsComment", "TestValue01"),),
        [
            *investigation_headers.STUDY_PROTOCOLS_KEYS[0:7],
            "Comment[ProtocolsComment]",
            *investigation_headers.STUDY_PROTOCOLS_KEYS[7:],
        ],
    )
    assert expected == study.protocols["metabolite extraction"]

    # Study 1 - Contacts
    assert 3 == len(study.contacts)
    expected = models.ContactInfo(
        "Juan",
        "Castrillo",
        "I",
        "",
        "123456789",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (models.Comment("Study Person REF", ""),),
        [*investigation_headers.STUDY_CONTACTS_KEYS, "Comment[Study Person REF]"],
    )
    assert expected == study.contacts[1]

    # Study 2
    study = investigation.studies[1]
    assert "BII-S-2" == study.info.identifier
    assert Path("s_BII-S-2.txt") == study.info.path
    assert "Study Grant Number" == study.info.comments[0].name
    assert "" == study.info.comments[0].value
    assert "Manuscript Licence" == study.info.comments[2].name
    assert "CC BY 3.0" == study.info.comments[2].value

    expected_headers = [
        *investigation_headers.STUDY_INFO_KEYS[0:3],
        "Comment[Study Grant Number]",
        "Comment[Study Funding Agency]",
        *investigation_headers.STUDY_INFO_KEYS[3:],
        "Comment[Manuscript Licence]",
        "Comment[Experimental Metadata Licence]",
        "Comment[Data Repository]",
        "Comment[Data Record Accession]",
        "Comment[Data Record URI]",
        "Comment[Supplementary Information File Name]",
        "Comment[Supplementary Information File Type]",
        "Comment[Supplementary File URI]",
        "Comment[Subject Keywords]",
    ]
    assert expected_headers == study.info.headers

    # Study 2 - Contacts
    assert 3 == len(study.contacts)
    expected = models.ContactInfo(
        "Juan",
        "Castrillo",
        "I",
        "",
        "123456789",
        "",
        "Oxford Road, Manchester M13 9PT, UK",
        "Faculty of Life Sciences, Michael Smith Building, " "University of Manchester",
        models.OntologyTermRef("author", "http://purl.obolibrary.org/obo/RoleO_0000061", "ROLEO"),
        (models.Comment("Study Person REF", "personB"),),
        [*investigation_headers.STUDY_CONTACTS_KEYS, "Comment[Study Person REF]"],
    )
    assert expected == study.contacts[1]


def test_parse_assays_investigation(assays_investigation_file):
    # Read Investigation from file-like object
    warnings.simplefilter("always")
    reader = InvestigationReader.from_stream(assays_investigation_file)
    with pytest.warns(IsaWarning) as record:
        investigation = reader.read()
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 7 == len(record)
    msg = "Removed trailing whitespaces in fields of line: ['Study Identifier', 's_assays ']"
    assert record[0].category == ParseIsatabWarning
    assert str(record[0].message) == msg
    msg = (
        "Removed trailing whitespaces in fields of line: ['Study Title', ' Minimal Germline Study']"
    )
    assert record[1].category == ParseIsatabWarning
    assert str(record[1].message) == msg
    msg = "No assays declared in study 's_assays' of investigation 'i_assays.txt'"
    assert record[2].category == AdvisoryIsaValidationWarning
    assert str(record[2].message) == msg
    msg = "Study identifier used more than once: s_assays"
    assert record[3].category == CriticalIsaValidationWarning
    assert str(record[3].message) == msg
    msg = "Study path used more than once: s_assays.txt"
    assert record[4].category == CriticalIsaValidationWarning
    assert str(record[4].message) == msg
    msg = "Study title used more than once: Minimal Germline Study"
    assert record[5].category == ModerateIsaValidationWarning
    assert str(record[5].message) == msg

    # Check results
    # Investigation
    assert investigation

    # Studies
    assert 2 == len(investigation.studies)

    # Assays
    assert 0 == len(investigation.studies[0].assays)
    assert 0 == len(investigation.studies[1].assays)


def test_parse_only_investigation(only_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(only_investigation_file)
    investigation = reader.read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    assert 1 == len(record)
    msg = "No studies declared in investigation: i_onlyinvest.txt"
    assert record[0].category == CriticalIsaValidationWarning
    assert str(record[0].message) == msg


def test_parse_warnings_investigation(warnings_investigation_file):
    # Read Investigation from file-like object
    reader = InvestigationReader.from_stream(warnings_investigation_file)
    investigation = reader.read()
    with pytest.warns(IsaWarning) as record:
        InvestigationValidator(investigation).validate()

    # Check warnings
    messages = [str(x.message) for x in record]
    print(messages)
    assert 15 == len(record)
    assert "Invalid mail address: invalid_mail" in messages
    assert "Invalid phone/fax number: CALL-ME" in messages
    assert "Invalid phone/fax number: FAX-ME" in messages
    assert "Invalid pubmed_id string: not-pubmed" in messages
    assert "Invalid doi string: not-a-doi" in messages
    assert "Assay path used more than once: a_warnings.txt" in messages
    assert [m for m in messages if m.startswith("Assay without platform")]
    assert 4 == len([m for m in messages if m.startswith("Incomplete ontology source")])

    # Check results
    # Investigation
    assert investigation

    # Ontology sources
    assert 5 == len(investigation.ontology_source_refs)
    expected = models.OntologyRef(
        "OBI",
        "http://data.bioontology.org/ontologies/OBI",
        "31",
        "Ontology for Biomedical Investigations",
        (),
        [*investigation_headers.ONTOLOGY_SOURCE_REF_KEYS],
    )
    assert expected == investigation.ontology_source_refs["OBI"]

    # Basic info
    assert "Investigation with Warnings" == investigation.info.title
    assert "i_warnings" == investigation.info.identifier

    # Studies
    assert len(investigation.studies) == 1
    assert "s_warnings" == investigation.studies[0].info.identifier
    assert "Germline Study with Warnings" == investigation.studies[0].info.title
    assert Path("s_warnings.txt") == investigation.studies[0].info.path

    # Assays
    assert len(investigation.studies[0].assays) == 2
    assay = investigation.studies[0].assays[0]
    assert Path("a_warnings.txt") == assay.path

    # Study contacts
    assert 0 == len(investigation.studies[0].contacts)

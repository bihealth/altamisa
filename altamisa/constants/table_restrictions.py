# -*- coding: utf-8 -*-
"""Constants used for validation of data and annotation restrictions in study and assay tables."""


__author__ = (
    "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>, "
    "Mathias Kuhring <mathias.kuhring@bihealth.de>"
)


from . import table_headers


# Assay measurement types (only the once needed for special validations)
PROTEIN_EXPRESSION_PROFILING = "protein expression profiling"  #:
PROTEIN_IDENTIFICATION = "protein identification"  #:
METABOLITE_PROFILING = "metabolite profiling"  #:


# Assay technology types (only the once needed for special validations)
DNA_MICROARRAY = "dna microarray"  #:
GEL_ELECTROPHORESIS = "gel electrophoresis"  #:
PROTEIN_MICROARRAY = "protein microarray"  #:
NUCLEOTIDE_SEQUENCING = "nucleotide sequencing"  #:
MASS_SPECTROMETRY = "mass spectrometry"  #:


# Protocol types (only the once needed for special validations)
PT_DATA_COLLECTION = "data collection"  #:
PT_DATA_NORMALIZATION = "data normalization"  #:
PT_DATA_TRANSFORMATION = "data transformation"  #:
PT_ELECTROPHORESIS = "electrophoresis"  #:
PT_HYBRIDIZATION = "hybridization"  #:
PT_MASS_SPECTROMETRY = "mass spectrometry"  #:
PT_NUCLEIC_ACID_HYBRIDIZATION = "nucleic acid hybridization"  #:


# Material restrictions ----------------------------------------------------------------------------


#: Materials restricted to certain assay technologies
RESTRICTED_MATERIALS_ATECH = {
    # nucleotide sequencing
    table_headers.LIBRARY_NAME: {NUCLEOTIDE_SEQUENCING}
}


#: Materials restricted to certain assay measurements
RESTRICTED_MATERIALS_AMEAS = {}


# Data file restrictions ---------------------------------------------------------------------------


#: Data files restricted to certain assay technologies
RESTRICTED_FILES_ATECH = {
    # microarray
    table_headers.ARRAY_DESIGN_FILE: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    table_headers.ARRAY_DATA_FILE: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    table_headers.ARRAY_DATA_MATRIX_FILE: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    table_headers.DERIVED_ARRAY_DATA_FILE: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    table_headers.DERIVED_ARRAY_DATA_MATRIX_FILE: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    # gel eletrophoresis
    table_headers.SPOT_PICKING_FILE: {GEL_ELECTROPHORESIS},
    # mass spectrometry
    table_headers.DERIVED_SPECTRAL_DATA_FILE: {MASS_SPECTROMETRY},
    table_headers.RAW_SPECTRAL_DATA_FILE: {MASS_SPECTROMETRY},
    table_headers.PEPTIDE_ASSIGNMENT_FILE: {MASS_SPECTROMETRY},
    table_headers.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE: {MASS_SPECTROMETRY},
    table_headers.PROTEIN_ASSIGNMENT_FILE: {MASS_SPECTROMETRY},
    table_headers.METABOLITE_ASSIGNMENT_FILE: {MASS_SPECTROMETRY},
}


#: Data files restricted to certain assay measurements
RESTRICTED_FILES_AMEAS = {
    # proteomics
    table_headers.PEPTIDE_ASSIGNMENT_FILE: {PROTEIN_EXPRESSION_PROFILING, PROTEIN_IDENTIFICATION},
    table_headers.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE: {
        PROTEIN_EXPRESSION_PROFILING,
        PROTEIN_IDENTIFICATION,
    },
    table_headers.PROTEIN_ASSIGNMENT_FILE: {PROTEIN_EXPRESSION_PROFILING, PROTEIN_IDENTIFICATION},
    # metabolomics
    table_headers.METABOLITE_ASSIGNMENT_FILE: {METABOLITE_PROFILING},
}


# Protocol restrictions ----------------------------------------------------------------------------


#: Protocol names restricted to certain assay technologies
RESTRICTED_PROTO_NAMES_ATECH = {
    # microarray
    table_headers.SCAN_NAME: {DNA_MICROARRAY, GEL_ELECTROPHORESIS, PROTEIN_MICROARRAY},
    table_headers.HYBRIDIZATION_ASSAY_NAME: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    # gel electrophoresis
    table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME: {GEL_ELECTROPHORESIS},
    # mass spectrometry
    table_headers.MS_ASSAY_NAME: {MASS_SPECTROMETRY},
}

#: Protocol names restricted by certain protocol types (ignored if ref is UNKNOWN)
RESTRICTED_PROTO_NAMES_PTYPE = {
    table_headers.DATA_TRANSFORMATION_NAME: {PT_DATA_TRANSFORMATION},
    table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME: {PT_ELECTROPHORESIS},
    table_headers.HYBRIDIZATION_ASSAY_NAME: {PT_HYBRIDIZATION, PT_NUCLEIC_ACID_HYBRIDIZATION},
    table_headers.MS_ASSAY_NAME: {PT_MASS_SPECTROMETRY},
    table_headers.NORMALIZATION_NAME: {PT_DATA_NORMALIZATION},
    table_headers.SCAN_NAME: {PT_DATA_COLLECTION},
}

#: Protocol special case annotations restricted to certain assay technologies
RESTRICTED_PROTO_ANNOS_ATECH = {
    # microarray
    table_headers.ARRAY_DESIGN_REF: {DNA_MICROARRAY, PROTEIN_MICROARRAY},
    # gel electrophoresis
    table_headers.FIRST_DIMENSION: {GEL_ELECTROPHORESIS},
    table_headers.SECOND_DIMENSION: {GEL_ELECTROPHORESIS},
}

#: Protocol special case annotations restricted to certain protocol types
RESTRICTED_PROTO_ANNOS_PTYPE = {
    table_headers.ARRAY_DESIGN_REF: {PT_HYBRIDIZATION, PT_NUCLEIC_ACID_HYBRIDIZATION},
    table_headers.FIRST_DIMENSION: {PT_ELECTROPHORESIS},
    table_headers.SECOND_DIMENSION: {PT_ELECTROPHORESIS},
}

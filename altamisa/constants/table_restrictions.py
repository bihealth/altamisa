# -*- coding: utf-8 -*-
"""Constants for data and annotation restrictions in study and assay tables"""


__author__ = (
    "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>, "
    "Mathias Kuhring <mathias.kuhring@bihealth.de>"
)


from . import table_headers


# Assay measurement types (only the once needed for special validations)
PROTEIN_EXPRESSION_PROFILING = "protein expression profiling"
PROTEIN_IDENTIFICATION = "protein identification"
METABOLITE_PROFILING = "metabolite profiling"


# Assay technology types (only the once needed for special validations)
DNA_MICROARRAY = "dna microarray"
GEL_ELECTROPHORESIS = "gel electrophoresis"
PROTEIN_MICROARRAY = "protein microarray"
MASS_SPECTROMETRY = "mass spectrometry"


# Data files restricted to assay technology
RESTRICTED_TECH_FILES = {
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


# Data files restricted to assay measurement
RESTRICTED_MEAS_FILES = {
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

# -*- coding: utf-8 -*-
"""
Constants of valid column headers for study and assay table parsing and writing,
as specified in the `ISA-Tab study and assay specifications
<https://isa-specs.readthedocs.io/en/latest/isatab.html#study-and-assay-files>`_.
"""


__author__ = (
    "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>, "
    "Mathias Kuhring <mathias.kuhring@bihealth.de>"
)


# The following constants are used for further qualifying column types of
# material and process nodes as well as annotations.


# Material types (nodes)
EXTRACT_NAME = "Extract Name"  #:
LABELED_EXTRACT_NAME = "Labeled Extract Name"  #:
LIBRARY_NAME = "Library Name"  #: Special material (see :ref:`special_extensions`)
SAMPLE_NAME = "Sample Name"  #:
SOURCE_NAME = "Source Name"  #:


# Data types (nodes)
ARRAY_DATA_FILE = "Array Data File"  #:
ARRAY_DATA_MATRIX_FILE = "Array Data Matrix File"  #:
ARRAY_DESIGN_FILE = "Array Design File"  #:
DERIVED_ARRAY_DATA_FILE = "Derived Array Data File"  #:
DERIVED_ARRAY_DATA_MATRIX_FILE = "Derived Array Data Matrix File"  #:
DERIVED_DATA_FILE = "Derived Data File"  #:
DERIVED_SPECTRAL_DATA_FILE = "Derived Spectral Data File"  #:
IMAGE_FILE = "Image File"  #:
METABOLITE_ASSIGNMENT_FILE = "Metabolite Assignment File"  #:
PEPTIDE_ASSIGNMENT_FILE = "Peptide Assignment File"  #:
POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE = (
    "Post Translational Modification Assignment File"
)  #:
PROTEIN_ASSIGNMENT_FILE = "Protein Assignment File"  #:
RAW_DATA_FILE = "Raw Data File"  #:
RAW_SPECTRAL_DATA_FILE = "Raw Spectral Data File"  #:
SPOT_PICKING_FILE = "Spot Picking File"  #:


# Assay types (nodes)
ASSAY_NAME = "Assay Name"  #:
DATA_TRANSFORMATION_NAME = "Data Transformation Name"  #:
GEL_ELECTROPHORESIS_ASSAY_NAME = "Gel Electrophoresis Assay Name"  #:
HYBRIDIZATION_ASSAY_NAME = "Hybridization Assay Name"  #:
MS_ASSAY_NAME = "MS Assay Name"  #:
NORMALIZATION_NAME = "Normalization Name"  #:
PROTOCOL_REF = "Protocol REF"  #:
SCAN_NAME = "Scan Name"  #:


# Other simple types (standard annotations)
DATE = "Date"  #:
LABEL = "Label"  #:
MATERIAL_TYPE = "Material Type"  #:
PERFORMER = "Performer"  #:
TERM_SOURCE_REF = "Term Source REF"  #:
TERM_ACCESSION_NUMBER = "Term Accession Number"  #:
UNIT = "Unit"  #:


# Other simple types (special case annotations)
ARRAY_DESIGN_REF = "Array Design REF"  #:
FIRST_DIMENSION = "First Dimension"  #:
SECOND_DIMENSION = "Second Dimension"  #:


# Labeled types (annotations)
CHARACTERISTICS = "Characteristics"  #:
COMMENT = "Comment"  #:
FACTOR_VALUE = "Factor Value"  #:
PARAMETER_VALUE = "Parameter Value"  #:


#: Collected header keys indicating a data file.
DATA_FILE_HEADERS = (
    ARRAY_DATA_FILE,
    ARRAY_DATA_MATRIX_FILE,
    ARRAY_DESIGN_FILE,
    DERIVED_ARRAY_DATA_FILE,
    DERIVED_ARRAY_DATA_MATRIX_FILE,
    DERIVED_DATA_FILE,
    DERIVED_SPECTRAL_DATA_FILE,
    IMAGE_FILE,
    METABOLITE_ASSIGNMENT_FILE,
    PEPTIDE_ASSIGNMENT_FILE,
    POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE,
    PROTEIN_ASSIGNMENT_FILE,
    RAW_DATA_FILE,
    RAW_SPECTRAL_DATA_FILE,
    SPOT_PICKING_FILE,
)


#: Collected header keys indicating a material/data name.
MATERIAL_NAME_HEADERS = (
    # Material
    EXTRACT_NAME,
    LABELED_EXTRACT_NAME,
    LIBRARY_NAME,
    SAMPLE_NAME,
    SOURCE_NAME,
    # Data
    *DATA_FILE_HEADERS,
)


#: Collected header keys indicating a process name.
PROCESS_NAME_HEADERS = (
    ASSAY_NAME,
    DATA_TRANSFORMATION_NAME,
    GEL_ELECTROPHORESIS_ASSAY_NAME,
    HYBRIDIZATION_ASSAY_NAME,
    MS_ASSAY_NAME,
    NORMALIZATION_NAME,
    SCAN_NAME,
    # PROTOCOL_REF,  # is not a name header!
)

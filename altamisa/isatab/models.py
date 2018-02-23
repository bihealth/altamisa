# -*- coding: utf-8 -*-
"""Low-level models for representing ISA-Tab data structure as
``ImmutableTuple`` objects.

The objects is done by containment in lists (a tree-like structure) and by
string names only.  However, the tree is only built within one file (e.g.,
a list of all materials in a study or all comments for a material).
"""

from datetime import date
from pathlib import Path
from typing import Dict, Tuple, NamedTuple, Union

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

# Base types, used throughout -------------------------------------------------


class AnnotatedStr(str):
    """A ``str`` that can be flagged with values.

    .. doctest::

        >>> from altamisa.isatab.models import AnnotatedStr
        >>> x = AnnotatedStr('EMPTY', was_empty=True, value_no=1)
        >>> x
        'EMPTY'
        >>> hasattr(x, 'was_empty')
        True
        >>> x.was_empty
        True
        >>> hasattr(x, 'value_no')
        True
        >>> x.value_no
        1
    """

    def __new__(cls, value, *args, **kwargs):
        # Explicitly only pass value to the str constructor
        return super().__new__(cls, value)

    def __init__(self, value, **kwargs):
        # Everything else is initialized in the str initializer
        for key, value in kwargs.items():
            setattr(self, key, value)


class OntologyTermRef(NamedTuple):
    """Reference to a term into an ontology
    """

    #: Human-readable name of the term
    name: str
    #: The accession of the referenced term
    accession: str
    #: Name of the ontology (links to ``OntologyRef.name``)
    ontology_name: str


#: Shorcut for the commonly used "free text or reference to a term in an
#: ontology" idiom.
FreeTextOrTermRef = Union[OntologyTermRef, str]


# Types used in investigation files -------------------------------------------


class OntologyRef(NamedTuple):
    """Description of an ontology term source, as used for investigation file.
    """

    #: The name of the ontology (e.g., ``CEBI``)
    name: str
    #: Path to file or URI to ontology
    file: str
    #: Version of the ontology
    version: str
    #: Description of the ontology
    description: str


class BasicInfo(NamedTuple):
    """Basic metadata for an investigation or study (``INVESTIGATION``
    or ``STUDY``).
    """

    #: Path to the investigation or study file
    path: Path
    #: Investigation/Study identifier
    identifier: str
    #: Investigation/Study title
    title: str
    #: Investigation/Study description
    description: str
    #: Investigation/Study submission date
    submission_date: date
    #: Investigation/Study public release date
    public_release_date: date


class PublicationInfo(NamedTuple):
    """Information regarding an investigation publication
    (``INVESTIGATION PUBLICATIONS``).
    """

    #: Publication PubMed ID
    pubmed_id: str
    #: Publication DOI
    doi: str
    #: Publication author list string
    authors: str
    #: Publication title
    title: str


class ContactInfo(NamedTuple):
    """Investigation contact information"""

    #: Last name of contact
    last_name: str
    #: Middle initial of contact
    mid_initial: str
    #: First name of contact
    first_name: str
    #: Email of contact
    email: str
    #: Phone of contact
    phone: str
    #: Fax no. of contact
    fax: str
    #: Address of contact
    address: str
    #: Affiliation of contact
    affiliation: str
    #: Role of contact
    role: str


class FactorInfo(NamedTuple):
    """Study factor information"""

    #: Factor name
    name: str
    #: Factor type
    type: FreeTextOrTermRef


class AssayInfo(NamedTuple):
    """Study assay information"""

    #: Assay measurement type
    measurement_type: FreeTextOrTermRef
    #: Assay technology type
    technology_type: FreeTextOrTermRef
    #: Assay platform
    platform: str
    #: Path to assay file
    path: Path


class ProtocolComponentInfo(NamedTuple):
    """Protocol component information"""

    #: Protocol component name
    name: str
    #: Protocol component type
    type: FreeTextOrTermRef


class ProtocolInfo(NamedTuple):
    """Protocol information"""

    #: Protocol name
    name: str
    #: Protocol type
    type: FreeTextOrTermRef
    #: Protocol
    description: str
    #: Protocol URI
    uri: str
    #: Protocol version
    version: str
    #: Protocol parameters
    parameters: Tuple[FreeTextOrTermRef]
    #: Protocol components
    component: Tuple[ProtocolComponentInfo]
    #: Protocol contact lists
    contacts: Tuple[ContactInfo]


class StudyInfo(NamedTuple):
    """The full metadata regarding one study"""

    #: Basic study information
    info: BasicInfo
    #: Study designs by name
    designs: Dict[str, FreeTextOrTermRef]
    #: Publication list for study
    publications: Tuple[PublicationInfo]
    #: Study factors by name
    factors: Dict[str, FactorInfo]
    #: Study assays by name
    assays: Dict[str, AssayInfo]
    #: Study protocols by name
    protocols: Dict[str, ProtocolInfo]
    #: Study contact list
    contacts: Tuple[ContactInfo]


class InvestigationInfo(NamedTuple):
    """Representation of an ISA investigation"""

    #: Ontologies defined for investigation
    ontology_source_refs: Dict[str, OntologyRef]
    #: Basic information on investigation
    info: BasicInfo
    #: List of investigation publications
    publications: Tuple[PublicationInfo]
    #: Contact list for investigation
    contacts: Tuple[ContactInfo]
    #: Contact list for study
    studies: Tuple[StudyInfo]


# Types used in study and assay files -----------------------------------------

# The following constants are used for further qualifying process and material
# nodes.

# Material node type descriptions

# TODO: these could go away!

MATERIAL = 'material'

EXTRACT = 'extract'
LABELED_EXTRACT = 'labeled extract'
SAMPLE = 'sample'
SOURCE = 'source'

# Data node types

ARRAY_DATA_FILE = 'array_data_file'
ARRAY_DATA_MATRIX_FILE = 'array_data_matrix_file'
DERIVED_ARRAY_DATA_FILE = 'derived_array_data_file'
DERIVED_ARRAY_MATRIX_DATA_FILE = 'derived_array_matrix_data_file'
DERIVED_DATA_FILE = 'derived_data_file'
DERIVED_SPECTRAL_DATA_FILE = 'derived_spectral_data_file'
METABOLITE_ASSIGNMENT_FILE = 'METABOLITE_ASSIGNMENT_FILE'
PEPTIDE_ASSIGNMENT_FILE = 'PEPTIDE_ASSIGNMENT_FILE'
PROTEIN_ASSIGNMENT_FILE = 'PROTEIN_ASSIGNMENT_FILE'
POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE = (
    'POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE')
RAW_DATA_FILE = 'raw_data_file'
RAW_SPECTRAL_DATA_FILE = 'raw_spectral_data_file'

# Assay types

PROTOCOL_REF = 'protocol_ref'
ASSAY = 'assay'
DATA_NORMALIZATION = 'data_normalization'
DATA_TRANSFORMATION = 'data_transformation'
GEL_ELECTROPHORESIS_ASSAY = 'gel_electrophoresis'
HYBRIDIZATION_ASSAY = 'hybridization'
MS_ASSAY = 'mass_spectometry'
NORMALIZATION = 'normalization'


class Characteristics(NamedTuple):
    """Representation of a ``Characteristics[*]`` cell."""

    #: Characteristics name
    name: str
    #: Characteristics value
    value: FreeTextOrTermRef
    #: Characteristics unit
    unit: FreeTextOrTermRef


class FactorValue(NamedTuple):
    """Representation of a ``Factor Value[*]`` cell."""

    #: Factor name
    name: str
    #: Factor value
    value: FreeTextOrTermRef
    #: Factor value unit
    unit: FreeTextOrTermRef


class ParameterValue(NamedTuple):
    """Representation of a ``Parameter Value[*]`` cell."""

    #: Parameter name
    name: str
    #: Parameter value
    value: FreeTextOrTermRef
    #: Parameter value unit
    unit: FreeTextOrTermRef


class Comment(NamedTuple):
    """Representation of a ``Comment[*]`` cell."""

    #: Comment name
    name: str
    #: Comment value
    value: FreeTextOrTermRef
    #: Comment unit
    unit: FreeTextOrTermRef


class Material(NamedTuple):
    """Representation of a Material or Data node."""
    type: str
    #: The name of the material.
    #:
    #: In the case that the label was empty, an ``AnnotatedStr`` is used and
    #: the attribute ``was_empty`` is set to ``True``.  As a ``str`` is used
    #: otherwise, use ``getattr(m.name, 'was_empty', False)`` for obtaining
    #: this information reliably.
    name: str
    label: str
    #: Material characteristics
    characteristics: Tuple[Characteristics]
    #: Material comments
    comments: Tuple[Comment]
    #: Material factor values
    factor_values: Tuple[FactorValue]
    #: Material type
    material_type: FreeTextOrTermRef


class Process(NamedTuple):
    """Representation of a Process or Assay node."""

    #: Referenced to protocol name from investigation
    protocol_ref: str
    #: The name of the protocol.
    #:
    #: When "Protocol REF" is given without a further
    #: qualifying name, this is generated from the protocol reference and
    #: an auto-incrementing number.  In this case that the label was empty,
    #: an ``AnnotatedStr`` is used and the attribute ``was_empty`` is set to
    #: ``True``.  As a ``str`` is used otherwise, use
    #: ``getattr(m.name, 'was_empty', False)`` for obtaining this information
    #: reliably.
    name: str
    #: Process date
    date: date
    #: Performer of process
    performer: str
    #: Tuple of parameters values
    parameter_values: Tuple[ParameterValue]
    #: Tuple of process comments
    comments: Tuple[Comment]
    #: Array design reference
    array_design_ref: str
    #: Scan name of process
    scan_name: str


class Arc(NamedTuple):
    """Representation of an arc between two ``Material`` and/or ``Process``
    nodes.
    """

    #: The arc's tail name
    tail: str
    #: The arc's head name
    head: str


class Study(NamedTuple):
    """Representation of an ISA study."""

    #: Path to ISA study file
    file: Path
    #: The study's header
    header: Tuple
    #: A mapping from material name to ``Material`` object (``Data``
    #: is a kind of material)
    materials: Dict[str, Material]
    #: A mapping from process name to ``Process`` object
    processes: Dict[str, Process]
    #: The processing arcs
    arcs: Tuple[Arc]


class Assay(NamedTuple):
    """Representation of an ISA assay."""

    #: Path to ISA assay file
    file: Path
    #: The assay's header
    header: Tuple
    #: A mapping from material name to ``Material`` object (``Data``
    #: is a kind of material)
    materials: Dict[str, Material]
    #: A mapping from process name to ``Process`` object
    processes: Dict[str, Process]
    #: The processing arcs
    arcs: Tuple[Arc]

# -*- coding: utf-8 -*-
"""Low-level models for representing ISA-Tab data structure as
``ImmutableTuple`` objects.

The objects is done by containment in lists (a tree-like structure) and by
string names only.  However, the tree is only built within one file (e.g.,
a list of all materials in a study or all comments for a material).
"""

from collections import namedtuple
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple, NamedTuple, Union


__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"


# Base types, used throughout -------------------------------------------------


class AnnotatedStr(str):
    """A ``str`` that can be flagged with values.
    """

    def __new__(cls, value, *args, **kwargs):
        # Explicitly only pass value to the str constructor
        return super().__new__(cls, value)

    def __init__(self, value, **kwargs):
        # Everything else is initialized in the str initializer
        for key, value in kwargs.items():
            setattr(self, key, value)


class OntologyTermRef(namedtuple("OntologyTermRef", "name accession ontology_name")):
    """Reference to a term into an ontology
    """

    def __new__(cls, name, accession, ontology_name, ontology_refs=None):
        # If accession or ontology_name is available --> OntologyTermRef
        if ontology_name or accession:
            return super(cls, OntologyTermRef).__new__(cls, name, accession, ontology_name)
        # Only the name is available --> Text only OntologyTermRef
        elif name:
            return super(cls, OntologyTermRef).__new__(cls, name, None, None)
        # Nothing available --> Empty OntologyTermRef
        else:
            return super(cls, OntologyTermRef).__new__(cls, None, None, None)

    #: Human-readable name of the term
    name: str
    #: The accession of the referenced term
    accession: str
    #: Name of the ontology (links to ``OntologyRef.name``)
    ontology_name: str


#: Shortcut for the commonly used "free text or reference to a term in an
#: ontology" idiom.
FreeTextOrTermRef = Union[OntologyTermRef, str]


class Comment(NamedTuple):
    """Representation of a ``Comment[*]`` cell."""

    #: Comment name
    name: str
    #: Comment value
    value: str


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
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


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
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


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
    #: Publication status
    status: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


class ContactInfo(NamedTuple):
    """Investigation contact information"""

    #: Last name of contact
    last_name: str
    #: First name of contact
    first_name: str
    #: Middle initial of contact
    mid_initial: str
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
    role: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


class DesignDescriptorsInfo(NamedTuple):
    """Study design descriptors information"""

    #: Design descriptors type
    type: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


class FactorInfo(NamedTuple):
    """Study factor information"""

    #: Factor name
    name: str
    #: Factor type
    type: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


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
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


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
    parameters: Dict[str, FreeTextOrTermRef]
    #: Protocol components
    components: Dict[str, ProtocolComponentInfo]
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


class StudyInfo(NamedTuple):
    """The full metadata regarding one study"""

    #: Basic study information
    info: BasicInfo
    #: Study designs by name
    designs: Tuple[DesignDescriptorsInfo]
    #: Publication list for study
    publications: Tuple[PublicationInfo]
    #: Study factors by name
    factors: Dict[str, FactorInfo]
    #: Study assays
    assays: Tuple[AssayInfo]
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
    #: List of studies in this investigation
    studies: Tuple[StudyInfo]


# Types used in study and assay files -----------------------------------------


class Characteristics(NamedTuple):
    """Representation of a ``Characteristics[*]`` cell."""

    #: Characteristics name
    name: str
    #: Characteristics value
    value: List[FreeTextOrTermRef]
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
    value: List[FreeTextOrTermRef]
    #: Parameter value unit
    unit: FreeTextOrTermRef


class Material(NamedTuple):
    """Representation of a Material or Data node."""

    #: The type of node (i.e. column name)
    type: str
    #: The unique name of the material node.
    #: This is usually created with respect to study/assay and column.
    #: The unique name is necessary to distinguish materials of different type with potential
    #: overlaps in names. Otherwise graph representation might be incorrect (ambiguous arcs, loops)
    #: and the original relation of material and process not conclusively reproducible.
    unique_name: str
    #: Original name of a material or data file
    name: str
    #: The label of a Labeled Extract
    extract_label: FreeTextOrTermRef
    #: Material characteristics
    characteristics: Tuple[Characteristics]
    #: Material comments
    comments: Tuple[Comment]
    #: Material factor values
    factor_values: Tuple[FactorValue]
    #: Material type
    material_type: FreeTextOrTermRef
    #: Columns headers from/for ISA-tab parsing/writing
    headers: List[str]


class Process(NamedTuple):
    """Representation of a Process or Assay node."""

    #: Referenced to protocol name from investigation
    protocol_ref: str
    #: The unique name of the process node.
    #: This is usually created with respect to study/assay and column.
    #: The unique name is necessary to distinguish processes of different protocols with potential
    #: overlaps in names. Otherwise graph representation might be incorrect (ambiguous arcs, loops)
    #: and the original relation of material and process not conclusively reproducible.
    #: When "Protocol REF" is given without a further qualifying name, this is generated from the
    #: protocol reference with an auto-incrementing number.
    unique_name: str
    #: Original name of a process (e.g. from Assay Name etc.)
    name: str
    #: Type of original name (e.g. Assay Name)
    name_type: str
    #: Process date
    date: date
    #: Performer of process
    performer: str
    #: Tuple of parameters values
    parameter_values: Tuple[ParameterValue]
    #: Tuple of process comments
    comments: Tuple[Comment]

    array_design_ref: str
    """
    Array design reference (special case annotation)\n
    Technology types: "DNA microarray", "protein microarray"\n
    Protocol types: "nucleic acid hybridization", "hybridization"
    """
    first_dimension: FreeTextOrTermRef
    """
    First dimension (special case annotation, INSTEAD of Gel Electrophoresis Assay Name)\n
    Technology types: "gel electrophoresis"\n
    Protocol types: "electrophoresis"
    """
    second_dimension: FreeTextOrTermRef
    """
    Second dimension (special case annotation, INSTEAD of Gel Electrophoresis Assay Name)\n
    Technology types: "gel electrophoresis"\n
    Protocol types: "electrophoresis"
    """

    #: Columns headers from/for ISA-tab parsing/writing
    headers: List[str]


class Arc(NamedTuple):
    """Representation of an arc between two ``Material`` and/or ``Process`` nodes."""

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

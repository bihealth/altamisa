# -*- coding: utf-8 -*-
"""Low-level models for representing ISA-Tab data structure as ``ImmutableTuple`` objects.

The objects is done by containment in lists (a tree-like structure) and by string names only.
However, the tree is only built within one file (e.g., a list of all materials in a study or all
comments for a material).
"""

from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple, Union

import attr


__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"


# Base types, used throughout -------------------------------------------------


class AnnotatedStr(str):
    """A ``str`` that can be flagged with values.

    **Example Usage**

    >>> x = AnnotateStr("text", key1="value1", key2=2)
    >>> x
    "text"
    >>> x.key1
    "value1"
    >>> x.key2
    2
    """

    def __new__(cls, value, *args, **kwargs):
        # Explicitly only pass value to the str constructor
        return super().__new__(cls, value)

    def __init__(self, value, **kwargs):
        # Everything else is initialized in the str initializer
        for key, value in kwargs.items():
            setattr(self, key, value)


@attr.s(auto_attribs=True, frozen=True)
class OntologyTermRef:
    """Reference to a term into an ontology.

    Can be either initialized with

    - all three of a `name`, an `accession`, and an `ontology_name`
    - only a `name`
    - nothing (empty)
    """

    def __attrs_post_init__(self):
        """Ensure that the name/accession/ontology_name are initialized consistently.

        cf. http://www.attrs.org/en/stable/init.html#post-init-hook
        """
        if not self.ontology_name and not self.accession:
            if not self.name:
                object.__setattr__(self, "name", None)
            object.__setattr__(self, "accession", None)
            object.__setattr__(self, "ontology_name", None)

    #: Human-readable name of the term
    name: str = None
    #: The accession of the referenced term
    accession: str = None
    #: Name of the ontology (links to ``OntologyRef.name``)
    ontology_name: str = None


#: Shortcut for the commonly used "free text or reference to a term in an
#: ontology" idiom.
FreeTextOrTermRef = Union[OntologyTermRef, str]


@attr.s(auto_attribs=True, frozen=True)
class Comment:
    """Representation of a ``Comment[*]`` cell."""

    #: Comment name
    name: str
    #: Comment value
    value: str


# Types used in investigation files -------------------------------------------


@attr.s(auto_attribs=True, frozen=True)
class OntologyRef:
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


@attr.s(auto_attribs=True, frozen=True)
class BasicInfo:
    """Basic metadata for an investigation or study (``INVESTIGATION`` or ``STUDY``).
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


@attr.s(auto_attribs=True, frozen=True)
class PublicationInfo:
    """Information regarding an investigation publication (``INVESTIGATION PUBLICATIONS``).
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


@attr.s(auto_attribs=True, frozen=True)
class ContactInfo:
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


@attr.s(auto_attribs=True, frozen=True)
class DesignDescriptorsInfo:
    """Study design descriptors information"""

    #: Design descriptors type
    type: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


@attr.s(auto_attribs=True, frozen=True)
class FactorInfo:
    """Study factor information"""

    #: Factor name
    name: str
    #: Factor type
    type: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]
    #: Headers from/for ISA-tab parsing/writing
    headers: List[str]


@attr.s(auto_attribs=True, frozen=True)
class AssayInfo:
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


@attr.s(auto_attribs=True, frozen=True)
class ProtocolComponentInfo:
    """Protocol component information"""

    #: Protocol component name
    name: str
    #: Protocol component type
    type: FreeTextOrTermRef


@attr.s(auto_attribs=True, frozen=True)
class ProtocolInfo:
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


@attr.s(auto_attribs=True, frozen=True)
class StudyInfo:
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


@attr.s(auto_attribs=True, frozen=True)
class InvestigationInfo:
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


@attr.s(auto_attribs=True, frozen=True)
class Characteristics:
    """Representation of a ``Characteristics[*]`` cell."""

    #: Characteristics name
    name: str
    #: Characteristics value
    value: List[FreeTextOrTermRef]
    #: Characteristics unit
    unit: FreeTextOrTermRef


@attr.s(auto_attribs=True, frozen=True)
class FactorValue:
    """Representation of a ``Factor Value[*]`` cell."""

    #: Factor name
    name: str
    #: Factor value
    value: FreeTextOrTermRef
    #: Factor value unit
    unit: FreeTextOrTermRef


@attr.s(auto_attribs=True, frozen=True)
class ParameterValue:
    """Representation of a ``Parameter Value[*]`` cell."""

    #: Parameter name
    name: str
    #: Parameter value
    value: List[FreeTextOrTermRef]
    #: Parameter value unit
    unit: FreeTextOrTermRef


@attr.s(auto_attribs=True, frozen=True)
class Material:
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


@attr.s(auto_attribs=True, frozen=True)
class Process:
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


@attr.s(auto_attribs=True, frozen=True)
class Arc:
    """Representation of an arc between two ``Material`` and/or ``Process`` nodes."""

    #: The arc's tail name
    tail: str
    #: The arc's head name
    head: str

    # TODO: remove this again?
    def __getitem__(self, idx):
        if idx == 0:
            return self.tail
        elif idx == 1:
            return self.head
        else:
            raise IndexError("Invalid index: %d" % idx)  # pragma: no cover


@attr.s(auto_attribs=True, frozen=True)
class Study:
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


@attr.s(auto_attribs=True, frozen=True)
class Assay:
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

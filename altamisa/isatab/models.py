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
import re
from typing import Dict, Tuple, NamedTuple, Union

from ..exceptions import ParseIsatabException

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"

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


class OntologyTermRef(namedtuple("OntologyTermRef", "name accession ontology_name")):
    """Reference to a term into an ontology
    """

    def __new__(cls, name, accession, ontology_name, ontology_refs=None):
        # If accession or ontology_name is available --> OntologyTermRef
        if ontology_name or accession:
            # All three variables must be available
            if not all((name, ontology_name, accession)):
                tpl = (
                    "Incomplete ontology term reference:\n" "name: {}\nOntology: {}\nAccession: {}"
                )
                msg = tpl.format(
                    name if name else "?",
                    ontology_name if ontology_name else "?",
                    accession if accession else "?",
                )
                raise ParseIsatabException(msg)
            # Ontology_name need to reference an ontology source (if provided)
            if ontology_refs and ontology_name not in ontology_refs:
                tpl = 'Ontology with name "{}" not defined in investigation!'
                msg = tpl.format(ontology_name)
                raise ParseIsatabException(msg)
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
    value: FreeTextOrTermRef
    #: Comment unit
    unit: FreeTextOrTermRef


# Pattern and functions for validate strings
# DATE_PATTERN = re.compile("^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$")
MAIL_PATTERN = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$")
PHONE_PATTERN = re.compile("^\\+?[\\d /()-]+$")  # only checks characters!
DOI_PATTERN = re.compile("^(?:(?:DOI|doi):)?10[.][0-9]{4,}(?:[.][0-9]+)*/\\S+$")
PMID_PATTERN = re.compile("^\\d+$")


def _validate_mail_address(mail_address) -> str:
    """Helper function to validate mail strings"""
    if mail_address and not MAIL_PATTERN.match(mail_address):
        tpl = "Invalid mail address: {}"
        msg = tpl.format(mail_address)
        raise ParseIsatabException(msg)
    return mail_address


def _validate_phone_number(phone_number) -> str:
    """Helper function to validate phone/fax number strings"""
    if phone_number and not PHONE_PATTERN.match(phone_number):
        tpl = "Invalid phone/fax number: {}"
        msg = tpl.format(phone_number)
        raise ParseIsatabException(msg)
    return phone_number


def _validate_doi(doi) -> str:
    """Helper function to validate doi strings"""
    if doi and not DOI_PATTERN.match(doi):
        tpl = "Invalid doi string: {}"
        msg = tpl.format(doi)
        raise ParseIsatabException(msg)
    return doi


def _validate_pubmed_id(pubmed_id) -> str:
    """Helper function to validate pubmed id strings"""
    if pubmed_id and not PMID_PATTERN.match(pubmed_id):
        tpl = "Invalid pubmed_id string: {}"
        msg = tpl.format(pubmed_id)
        raise ParseIsatabException(msg)
    return pubmed_id


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


class PublicationInfo(namedtuple("PublicationInfo", "pubmed_id doi authors title status comments")):
    """Information regarding an investigation publication
    (``INVESTIGATION PUBLICATIONS``).
    """

    def __new__(cls, pubmed_id, doi, authors, title, status, comments):
        return super(cls, PublicationInfo).__new__(
            cls,
            _validate_pubmed_id(pubmed_id),
            _validate_doi(doi),
            authors,
            title,
            status,
            comments,
        )

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


class ContactInfo(
    namedtuple(
        "ContactInfo",
        "last_name first_name mid_initial email phone fax address affiliation role comments",
    )
):
    """Investigation contact information"""

    def __new__(
        cls,
        last_name,
        first_name,
        mid_initial,
        email,
        phone,
        fax,
        address,
        affiliation,
        role,
        comments,
    ):
        return super(cls, ContactInfo).__new__(
            cls,
            last_name,
            first_name,
            mid_initial,
            _validate_mail_address(email),
            _validate_phone_number(phone),
            _validate_phone_number(fax),
            address,
            affiliation,
            role,
            comments,
        )

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


class DesignDescriptorsInfo(NamedTuple):
    """Study design descriptors information"""

    #: Design descriptors type
    type: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]


class FactorInfo(NamedTuple):
    """Study factor information"""

    #: Factor name
    name: str
    #: Factor type
    type: FreeTextOrTermRef
    #: Comments
    comments: Tuple[Comment]


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


class StudyInfo(NamedTuple):
    """The full metadata regarding one study"""

    #: Basic study information
    info: BasicInfo
    #: Study designs by name
    designs: Tuple[FreeTextOrTermRef]
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


class Material(NamedTuple):
    """Representation of a Material or Data node."""

    type: str
    #: The unique name of the material node.
    #:
    #: In the case that the label was empty, an ``AnnotatedStr`` is used and
    #: the attribute ``was_empty`` is set to ``True``.  As a ``str`` is used
    #: otherwise, use ``getattr(m.name, 'was_empty', False)`` for obtaining
    #: this information reliably.
    unique_name: str
    # Original name of a material or data file
    name: str
    # The label of a Labeled Extract
    extract_label: FreeTextOrTermRef
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
    #: The unique name of the process node.
    #:
    #: When "Protocol REF" is given without a further
    #: qualifying name, this is generated from the protocol reference and
    #: an auto-incrementing number. In this case that the label was empty,
    #: an ``AnnotatedStr`` is used and the attribute ``was_empty`` is set to
    #: ``True``. As a ``str`` is used otherwise, use
    #: ``getattr(m.name, 'was_empty', False)`` for obtaining this information
    #: reliably.
    unique_name: str
    # Original name of a process (e.g. from Assay Name etc.)
    name: str
    # Type of original name (e.g. Assay Name)
    name_type: str
    #: Process date
    date: date
    #: Performer of process
    performer: str
    #: Tuple of parameters values
    parameter_values: Tuple[ParameterValue]
    #: Tuple of process comments
    comments: Tuple[Comment]

    #: Special case annotations
    #: Technology types: "DNA microarray", "protein microarray"
    #: Protocol types: "nucleic acid hybridization", "hybridization"
    #: Array design reference
    array_design_ref: str

    #: Technology types: "gel electrophoresis"
    #: Protocol types: "electrophoresis"
    #: First and second dimension (INSTEAD of Gel Electrophoresis Assay Name)
    first_dimension: FreeTextOrTermRef
    second_dimension: FreeTextOrTermRef


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

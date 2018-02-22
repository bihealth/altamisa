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

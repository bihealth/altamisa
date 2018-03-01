# -*- coding: utf-8 -*-
"""Code for parsing investigation files.
"""

import os
import csv
from pathlib import Path
from typing import Iterator, TextIO
import warnings

from . import models
from ..exceptions import ParseIsatabException, ParseIsatabWarning

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


# We define constants for the headers in the investigation file as a typo in
# the code below can then be caught as "unknown identifier" instead of having
# to chase down string mismatches in if/then/else or table lookups.
ONTOLOGY_SOURCE_REFERENCE = 'ONTOLOGY SOURCE REFERENCE'
INVESTIGATION = 'INVESTIGATION'
INVESTIGATION_PUBLICATIONS = 'INVESTIGATION PUBLICATIONS'
INVESTIGATION_CONTACTS = 'INVESTIGATION CONTACTS'
STUDY = 'STUDY'
STUDY_DESIGN_DESCRIPTORS = 'STUDY DESIGN DESCRIPTORS'
STUDY_PUBLICATIONS = 'STUDY PUBLICATIONS'
STUDY_FACTORS = 'STUDY FACTORS'
STUDY_ASSAYS = 'STUDY ASSAYS'
STUDY_PROTOCOLS = 'STUDY PROTOCOLS'
STUDY_CONTACTS = 'STUDY CONTACTS'


# ONTOLOGY SOURCE REFERENCE
TERM_SOURCE_NAME = 'Term Source Name'
TERM_SOURCE_FILE = 'Term Source File'
TERM_SOURCE_VERSION = 'Term Source Version'
TERM_SOURCE_DESCRIPTION = 'Term Source Description'
ONTOLOGY_SOURCE_REF_KEYS = (
    TERM_SOURCE_NAME,
    TERM_SOURCE_FILE,
    TERM_SOURCE_VERSION,
    TERM_SOURCE_DESCRIPTION)


# INVESTIGATION (basic info)
INVESTIGATION_IDENTIFIER = 'Investigation Identifier'
INVESTIGATION_TITLE = 'Investigation Title'
INVESTIGATION_DESCRIPTION = 'Investigation Description'
INVESTIGATION_SUBMISSION_DATE = 'Investigation Submission Date'
INVESTIGATION_PUBLIC_RELEASE_DATE = 'Investigation Public Release Date'
INVESTIGATION_INFO_KEYS = (
    INVESTIGATION_IDENTIFIER,
    INVESTIGATION_TITLE,
    INVESTIGATION_DESCRIPTION,
    INVESTIGATION_SUBMISSION_DATE,
    INVESTIGATION_PUBLIC_RELEASE_DATE)


# INVESTIGATION PUBLICATIONS
INVESTIGATION_PUBMED_ID = 'Investigation PubMed ID'
INVESTIGATION_PUBLICATION_DOI = 'Investigation Publication DOI'
INVESTIGATION_PUBLICATION_AUTHOR_LIST = 'Investigation Publication Author List'
INVESTIGATION_PUBLICATION_TITLE = 'Investigation Publication Title'
INVESTIGATION_PUBLICATION_STATUS = 'Investigation Publication Status'
INVESTIGATION_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER = (
    'Investigation Publication Status Term Accession Number')
INVESTIGATION_PUBLICATION_STATUS_TERM_SOURCE_REF = (
    'Investigation Publication Status Term Source REF')
INVESTIGATION_PUBLICATIONS_KEYS = (
    INVESTIGATION_PUBMED_ID,
    INVESTIGATION_PUBLICATION_DOI,
    INVESTIGATION_PUBLICATION_AUTHOR_LIST,
    INVESTIGATION_PUBLICATION_TITLE,
    INVESTIGATION_PUBLICATION_STATUS,
    INVESTIGATION_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER,
    INVESTIGATION_PUBLICATION_STATUS_TERM_SOURCE_REF)


# INVESTIGATION CONTACTS
INVESTIGATION_PERSON_LAST_NAME = 'Investigation Person Last Name'
INVESTIGATION_PERSON_FIRST_NAME = 'Investigation Person First Name'
INVESTIGATION_PERSON_MID_INITIALS = 'Investigation Person Mid Initials'
INVESTIGATION_PERSON_EMAIL = 'Investigation Person Email'
INVESTIGATION_PERSON_PHONE = 'Investigation Person Phone'
INVESTIGATION_PERSON_FAX = 'Investigation Person Fax'
INVESTIGATION_PERSON_ADDRESS = 'Investigation Person Address'
INVESTIGATION_PERSON_AFFILIATION = 'Investigation Person Affiliation'
INVESTIGATION_PERSON_ROLES = 'Investigation Person Roles'
INVESTIGATION_PERSON_ROLES_TERM_ACCESSION_NUMBER = (
    'Investigation Person Roles Term Accession Number')
INVESTIGATION_PERSON_ROLES_TERM_SOURCE_REF = (
    'Investigation Person Roles Term Source REF')
INVESTIGATION_CONTACTS_KEYS = (
    INVESTIGATION_PERSON_LAST_NAME,
    INVESTIGATION_PERSON_FIRST_NAME,
    INVESTIGATION_PERSON_MID_INITIALS,
    INVESTIGATION_PERSON_EMAIL,
    INVESTIGATION_PERSON_PHONE,
    INVESTIGATION_PERSON_FAX,
    INVESTIGATION_PERSON_ADDRESS,
    INVESTIGATION_PERSON_AFFILIATION,
    INVESTIGATION_PERSON_ROLES,
    INVESTIGATION_PERSON_ROLES_TERM_ACCESSION_NUMBER,
    INVESTIGATION_PERSON_ROLES_TERM_SOURCE_REF)


# STUDY (basic info)
STUDY_IDENTIFIER = 'Study Identifier'
STUDY_TITLE = 'Study Title'
STUDY_DESCRIPTION = 'Study Description'
STUDY_SUBMISSION_DATE = 'Study Submission Date'
STUDY_PUBLIC_RELEASE_DATE = 'Study Public Release Date'
STUDY_FILE_NAME = 'Study File Name'
STUDY_INFO_KEYS = (
    STUDY_IDENTIFIER,
    STUDY_TITLE,
    STUDY_DESCRIPTION,
    STUDY_SUBMISSION_DATE,
    STUDY_PUBLIC_RELEASE_DATE,
    STUDY_FILE_NAME)


# STUDY DESIGN DESCRIPTORS
STUDY_DESIGN_TYPE = 'Study Design Type'
STUDY_DESIGN_TYPE_TERM_ACCESSION_NUMBER = (
    'Study Design Type Term Accession Number')
STUDY_DESIGN_TYPE_TERM_SOURCE_REF = 'Study Design Type Term Source REF'
STUDY_DESIGN_DESCR_KEYS = (
    STUDY_DESIGN_TYPE,
    STUDY_DESIGN_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_DESIGN_TYPE_TERM_SOURCE_REF)


# STUDY PUBLICATIONS
STUDY_PUBMED_ID = 'Study PubMed ID'
STUDY_PUBLICATION_DOI = 'Study Publication DOI'
STUDY_PUBLICATION_AUTHOR_LIST = 'Study Publication Author List'
STUDY_PUBLICATION_TITLE = 'Study Publication Title'
STUDY_PUBLICATION_STATUS = 'Study Publication Status'
STUDY_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER = (
    'Study Publication Status Term Accession Number')
STUDY_PUBLICATION_STATUS_TERM_SOURCE_REF = (
    'Study Publication Status Term Source REF')
STUDY_PUBLICATIONS_KEYS = (
    STUDY_PUBMED_ID,
    STUDY_PUBLICATION_DOI,
    STUDY_PUBLICATION_AUTHOR_LIST,
    STUDY_PUBLICATION_TITLE,
    STUDY_PUBLICATION_STATUS,
    STUDY_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER,
    STUDY_PUBLICATION_STATUS_TERM_SOURCE_REF)


# STUDY FACTORS
STUDY_FACTOR_NAME = 'Study Factor Name'
STUDY_FACTOR_TYPE = 'Study Factor Type'
STUDY_FACTOR_TYPE_TERM_ACCESSION_NUMBER = (
    'Study Factor Type Term Accession Number')
STUDY_FACTOR_TYPE_TERM_SOURCE_REF = 'Study Factor Type Term Source REF'
STUDY_FACTORS_KEYS = (
    STUDY_FACTOR_NAME,
    STUDY_FACTOR_TYPE,
    STUDY_FACTOR_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_FACTOR_TYPE_TERM_SOURCE_REF)


# STUDY ASSAYS
STUDY_ASSAY_FILE_NAME = 'Study Assay File Name'
STUDY_ASSAY_MEASUREMENT_TYPE = 'Study Assay Measurement Type'
STUDY_ASSAY_MEASUREMENT_TYPE_TERM_ACCESSION_NUMBER = (
    'Study Assay Measurement Type Term Accession Number')
STUDY_ASSAY_MEASUREMENT_TYPE_TERM_SOURCE_REF = (
    'Study Assay Measurement Type Term Source REF')
STUDY_ASSAY_TECHNOLOGY_TYPE = 'Study Assay Technology Type'
STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_ACCESSION_NUMBER = (
    'Study Assay Technology Type Term Accession Number')
STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_SOURCE_REF = (
    'Study Assay Technology Type Term Source REF')
STUDY_ASSAY_TECHNOLOGY_PLATFORM = 'Study Assay Technology Platform'
STUDY_ASSAYS_KEYS = (
    STUDY_ASSAY_FILE_NAME,
    STUDY_ASSAY_MEASUREMENT_TYPE,
    STUDY_ASSAY_MEASUREMENT_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_ASSAY_MEASUREMENT_TYPE_TERM_SOURCE_REF,
    STUDY_ASSAY_TECHNOLOGY_TYPE,
    STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_SOURCE_REF,
    STUDY_ASSAY_TECHNOLOGY_PLATFORM)


# STUDY PROTOCOLS
STUDY_PROTOCOL_NAME = 'Study Protocol Name'
STUDY_PROTOCOL_TYPE = 'Study Protocol Type'
STUDY_PROTOCOL_TYPE_TERM_ACCESSION_NUMBER = (
    'Study Protocol Type Term Accession Number')
STUDY_PROTOCOL_TYPE_TERM_SOURCE_REF = 'Study Protocol Type Term Source REF'
STUDY_PROTOCOL_DESCRIPTION = 'Study Protocol Description'
STUDY_PROTOCOL_URI = 'Study Protocol URI'
STUDY_PROTOCOL_VERSION = 'Study Protocol Version'
STUDY_PROTOCOL_PARAMETERS_NAME = 'Study Protocol Parameters Name'
STUDY_PROTOCOL_PARAMETERS_NAME_TERM_ACCESSION_NUMBER = (
    'Study Protocol Parameters Name Term Accession Number')
STUDY_PROTOCOL_PARAMETERS_NAME_TERM_SOURCE_REF = (
    'Study Protocol Parameters Name Term Source REF')
STUDY_PROTOCOL_COMPONENTS_NAME = 'Study Protocol Components Name'
STUDY_PROTOCOL_COMPONENTS_TYPE = 'Study Protocol Components Type'
STUDY_PROTOCOL_COMPONENTS_TYPE_TERM_ACCESSION_NUMBER = (
    'Study Protocol Components Type Term Accession Number')
STUDY_PROTOCOL_COMPONENTS_TYPE_TERM_SOURCE_REF = (
    'Study Protocol Components Type Term Source REF')
STUDY_PROTOCOLS_KEYS = (
    STUDY_PROTOCOL_NAME,
    STUDY_PROTOCOL_TYPE,
    STUDY_PROTOCOL_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_PROTOCOL_TYPE_TERM_SOURCE_REF,
    STUDY_PROTOCOL_DESCRIPTION,
    STUDY_PROTOCOL_URI,
    STUDY_PROTOCOL_VERSION,
    STUDY_PROTOCOL_PARAMETERS_NAME,
    STUDY_PROTOCOL_PARAMETERS_NAME_TERM_ACCESSION_NUMBER,
    STUDY_PROTOCOL_PARAMETERS_NAME_TERM_SOURCE_REF,
    STUDY_PROTOCOL_COMPONENTS_NAME,
    STUDY_PROTOCOL_COMPONENTS_TYPE,
    STUDY_PROTOCOL_COMPONENTS_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_PROTOCOL_COMPONENTS_TYPE_TERM_SOURCE_REF)


# STUDY CONTACTS
STUDY_PERSON_LAST_NAME = 'Study Person Last Name'
STUDY_PERSON_FIRST_NAME = 'Study Person First Name'
STUDY_PERSON_MID_INITIALS = 'Study Person Mid Initials'
STUDY_PERSON_EMAIL = 'Study Person Email'
STUDY_PERSON_PHONE = 'Study Person Phone'
STUDY_PERSON_FAX = 'Study Person Fax'
STUDY_PERSON_ADDRESS = 'Study Person Address'
STUDY_PERSON_AFFILIATION = 'Study Person Affiliation'
STUDY_PERSON_ROLES = 'Study Person Roles'
STUDY_PERSON_ROLES_TERM_ACCESSION_NUMBER = (
    'Study Person Roles Term Accession Number')
STUDY_PERSON_ROLES_TERM_SOURCE_REF = 'Study Person Roles Term Source REF'
STUDY_CONTACTS_KEYS = (
    STUDY_PERSON_LAST_NAME,
    STUDY_PERSON_FIRST_NAME,
    STUDY_PERSON_MID_INITIALS,
    STUDY_PERSON_EMAIL,
    STUDY_PERSON_PHONE,
    STUDY_PERSON_FAX,
    STUDY_PERSON_ADDRESS,
    STUDY_PERSON_AFFILIATION,
    STUDY_PERSON_ROLES,
    STUDY_PERSON_ROLES_TERM_ACCESSION_NUMBER,
    STUDY_PERSON_ROLES_TERM_SOURCE_REF)


# Helper function to extract comment headers and values from a section dict
def _parse_comments(section, comment_keys, i=None):
    def _parse_comment_header(val):
        # key might start with "Comment[" or "Comment ["
        tok = val[len('Comment'):].strip()
        if not tok or tok[0] != '[' or tok[-1] != ']':
            tpl = 'Problem parsing comment header {}'
            msg = tpl.format(tpl.format(val))
            raise ParseIsatabException(msg)
        return tok[1:-1]

    if i is not None:
        comments = {_parse_comment_header(k):
                    section[k][i] for k in comment_keys}
    else:
        comments = {_parse_comment_header(k):
                    section[k] for k in comment_keys}
    return comments


# Helper function to extract protocol parameters
def _split_study_protocols_parameters(
    names, name_term_accs, name_term_srcs, ontology_refs) -> Iterator[
        models.FreeTextOrTermRef]:
    names = names.split(';')
    name_term_accs = name_term_accs.split(';')
    name_term_srcs = name_term_srcs.split(';')
    if not (len(names) == len(name_term_accs) == len(name_term_srcs)):
        tpl = 'Unequal protocol parameter splits; found: "{}", "{}", "{}"'
        msg = tpl.format(names, name_term_accs, name_term_srcs)
        raise ParseIsatabException(msg)
    if len(names) > len(set(names)):
        tpl = 'Repeated protocol parameter; found: {}'
        msg = tpl.format(names)
        raise ParseIsatabException(msg)
    for (name, acc, src) in zip(names, name_term_accs, name_term_srcs):
        if any((name, acc, src)):  # skips empty parameters
            yield models.build_freetext_or_term_ref(name, acc, src,
                                                    ontology_refs)


# Helper function to extract protocol components
def _split_study_protocols_components(
    names, types, type_term_accs, type_term_srcs, ontology_refs) -> Iterator[
        models.ProtocolComponentInfo]:
    names = names.split(';')
    types = types.split(';')
    type_term_accs = type_term_accs.split(';')
    type_term_srcs = type_term_srcs.split(';')
    if not (len(names) == len(types)
            == len(type_term_accs) == len(type_term_srcs)):
        tpl = ('Unequal protocol component splits; '
               'found: "{}", "{}", "{}", "{}"')
        msg = tpl.format(names, types, type_term_accs, type_term_srcs)
        raise ParseIsatabException(msg)
    if len(names) > len(set(names)):
        tpl = 'Repeated protocol components; found: {}'
        msg = tpl.format(names)
        raise ParseIsatabException(msg)
    for (name, ctype, acc, src) in zip(
            names, types, type_term_accs, type_term_srcs):
        if any((name, ctype, acc, src)):  # skips empty components
            yield models.ProtocolComponentInfo(
                name,
                models.build_freetext_or_term_ref(ctype, acc, src,
                                                  ontology_refs))


class InvestigationReader:
    """Helper class that reads an investigation file into a
    ``InvestigationInfo`` object.
    """

    @classmethod
    def from_stream(self, input_file: TextIO):
        """Construct from file-like object"""
        return InvestigationReader(input_file)

    def __init__(self, input_file: TextIO):
        self.input_file = input_file
        self._reader = csv.reader(input_file, delimiter='\t', quotechar='"')
        self._line = None
        self._read_next_line()
        self._ontology_refs = None

    def _read_next_line(self):
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        try:
            self._line = next(self._reader)
            while self._line is not None and (
                    not self._line or self._line[0].startswith('#')):
                self._line = next(self._reader)
        except StopIteration:
            self._line = None
        return prev_line

    def _next_line_startswith_comment(self):
        if not self._line:
            return False
        else:
            return self._line[0].startswith('Comment')

    def _next_line_startswith(self, token):
        """Return whether line starts with ``token``"""
        if not self._line:
            return False
        else:
            return self._line[0].startswith(token)

    def read(self) -> models.InvestigationInfo:
        """Read investigation file"""
        self._ontology_refs = {
            o.name: o for o in self._read_ontology_source_reference()}
        info = self._read_basic_info()
        publications = list(self._read_publications())
        contacts = list(self._read_contacts())
        studies = list(self._read_studies())
        return models.InvestigationInfo(
            self._ontology_refs, info, publications, contacts, studies)

    # reader for content of sections with possibly multiple columns
    # i.e. ONTOLOGY SOURCE REFERENCE, INVESTIGATION PUBLICATIONS,
    # INVESTIGATION CONTACTS, STUDY DESIGN DESCRIPTORS, STUDY PUBLICATIONS,
    # STUDY FACTORS, STUDY ASSAYS, STUDY PROTOCOLS, STUDY CONTACTS
    def _read_multi_column_section(self, prefix, ref_keys, section_name):
        section = {}
        comment_keys = set()
        while (self._next_line_startswith(prefix) or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            key = line[0]
            if key.startswith('Comment'):
                comment_keys.add(key)
            elif key not in ref_keys:
                tpl = 'Line must start with one of {} but is {}'
                msg = tpl.format(ref_keys, line)
                raise ParseIsatabException(msg)
            if key in section:
                tpl = 'Key {} repeated, previous value "{}"'
                msg = tpl.format(key, section[key])
                raise ParseIsatabException(msg)
            section[key] = line[1:]
        # Check that all keys are given and all contain the same number of
        # entries
        if len(section) != len(ref_keys) + len(comment_keys):
            tpl = 'Missing entries in section {}; found: {}'
            msg = tpl.format(section_name, list(sorted(section)))
            raise ParseIsatabException(msg)
        if not len(set([len(v) for v in section.values()])) == 1:
            tpl = 'Inconsistent entry lengths in section {}'
            msg = tpl.format(section_name)
            raise ParseIsatabException(msg)
        return section, comment_keys

    # reader for content of a section with only one column
    # i.e. INVESTIGATION and STUDY
    def _read_single_column_section(self, prefix, ref_keys, section_name):
        # Read the lines in this section.
        section = {}
        comment_keys = set()
        while (self._next_line_startswith(prefix) or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if len(line) > 2:
                tpl = 'Line {} contains more than one value: {}'
                msg = tpl.format(line[0], line[1:])
                raise ParseIsatabException(msg)
            key = line[0]
            if key.startswith('Comment'):
                comment_keys.add(key)
            elif key not in ref_keys:
                tpl = 'Line must start with one of {} but is {}'
                msg = tpl.format(ref_keys, line)
                raise ParseIsatabException(msg)
            if key in section:
                tpl = 'Key {} repeated, previous value "{}"'
                msg = tpl.format(key, section[key])
                raise ParseIsatabException(msg)
            # read value if field is available, empty string else
            section[key] = line[1] if len(line) > 1 else ''
        # Check that all keys are given
        if len(section) != len(ref_keys) + len(comment_keys):
            tpl = 'Missing entries in section {}; found: {}'
            msg = tpl.format(section_name, list(sorted(section)))
            raise ParseIsatabException(msg)
        return section, comment_keys

    def _read_ontology_source_reference(self) -> Iterator[
            models.OntologyRef]:
        # Read ONTOLOGY SOURCE REFERENCE header
        line = self._read_next_line()
        if not line[0] == ONTOLOGY_SOURCE_REFERENCE:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(ONTOLOGY_SOURCE_REFERENCE, line)
            raise ParseIsatabException(msg)
        # Read the other four lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Term Source', ONTOLOGY_SOURCE_REF_KEYS, ONTOLOGY_SOURCE_REFERENCE)
        # Create resulting objects
        columns = zip(*(section[k] for k in ONTOLOGY_SOURCE_REF_KEYS))
        for i, (name, file_, version, desc) in enumerate(columns):
            # If ontology source is empty, skip it
            # (since ISAcreator always adds a last empty ontology column)
            if not any((name, file_, version, desc)):
                tpl = 'Skipping empty ontology source: {}, {}, {}, {}'
                msg = tpl.format(name, file_, version, desc)
                warnings.warn(msg, ParseIsatabWarning)
                continue
            # Check if ontology source is complete
            if not all((name, file_, version, desc)):
                tpl = 'Incomplete ontology source; found: {}, {}, {}, {}'
                msg = tpl.format(name, file_, version, desc)
                raise ParseIsatabException(msg)
            comments = _parse_comments(section, comment_keys, i)
            yield models.OntologyRef(name, file_, version, desc, comments)

    def _read_basic_info(self) -> models.BasicInfo:
        # Read INVESTIGATION header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_single_column_section(
            'Investigation', INVESTIGATION_INFO_KEYS, INVESTIGATION)
        # Create resulting object
        # TODO: do we really need the name of the investigation file?
        comments = _parse_comments(section, comment_keys)
        return models.BasicInfo(Path(os.path.basename(self.input_file.name)),
                                section[INVESTIGATION_IDENTIFIER],
                                section[INVESTIGATION_TITLE],
                                section[INVESTIGATION_DESCRIPTION],
                                section[INVESTIGATION_SUBMISSION_DATE],
                                section[INVESTIGATION_PUBLIC_RELEASE_DATE],
                                comments)

    def _read_publications(self) -> Iterator[models.PublicationInfo]:
        # Read INVESTIGATION PUBLICATIONS header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION_PUBLICATIONS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION_PUBLICATIONS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Investigation Pub',
            INVESTIGATION_PUBLICATIONS_KEYS,
            INVESTIGATION_PUBLICATIONS)
        # Create resulting objects
        columns = zip(*(section[k] for k in INVESTIGATION_PUBLICATIONS_KEYS))
        for i, (pubmed_id, doi, authors, title,
                status_term, status_term_acc, status_term_src) \
                in enumerate(columns):
            status = models.build_freetext_or_term_ref(
                status_term, status_term_acc,
                status_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.PublicationInfo(
                pubmed_id, doi, authors, title, status, comments)

    def _read_contacts(self) -> Iterator[models.ContactInfo]:
        # Read INVESTIGATION CONTACTS header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION_CONTACTS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION_CONTACTS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Investigation Person',
            INVESTIGATION_CONTACTS_KEYS,
            INVESTIGATION_CONTACTS)
        # Create resulting objects
        columns = zip(
            *(section[k] for k in INVESTIGATION_CONTACTS_KEYS))
        for i, (last_name, first_name, mid_initial, email, phone, fax, address,
                affiliation, role_term, role_term_acc, role_term_src) in \
                enumerate(columns):
            role = models.build_freetext_or_term_ref(
                role_term, role_term_acc, role_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.ContactInfo(
                last_name, first_name, mid_initial, email, phone, fax, address,
                affiliation, role, comments)

    def _read_studies(self) -> Iterator[models.StudyInfo]:
        # TODO: is it legal to have no study in the investigation?
        while self._line:
            # Read STUDY header
            line = self._read_next_line()
            if not line[0] == STUDY:
                tpl = 'Expected {} but got {}'
                msg = tpl.format(INVESTIGATION, line)
                raise ParseIsatabException(msg)
            # Read the other lines in this section.
            section, comment_keys = self._read_single_column_section(
                'Study', STUDY_INFO_KEYS, STUDY)
            # From this, parse the basic information from the study
            comments = _parse_comments(section, comment_keys)
            basic_info = models.BasicInfo(Path(section[STUDY_FILE_NAME]),
                                          section[STUDY_IDENTIFIER],
                                          section[STUDY_TITLE],
                                          section[STUDY_DESCRIPTION],
                                          section[STUDY_SUBMISSION_DATE],
                                          section[STUDY_PUBLIC_RELEASE_DATE],
                                          comments)
            # Read the remaining sections for this study
            # TODO: specs says "order MAY vary"
            design_descriptors = tuple(self._read_study_design_descriptors())
            publications = tuple(self._read_study_publications())
            factors = {f.name: f for f in self._read_study_factors()}
            assays = {a.path.name: a for a in self._read_study_assays()}
            protocols = {p.name: p for p in self._read_study_protocols()}
            contacts = tuple(self._read_study_contacts())
            # Create study object
            yield models.StudyInfo(
                basic_info, design_descriptors, publications, factors,
                assays, protocols, contacts)

    def _read_study_design_descriptors(self) -> Iterator[
            models.FreeTextOrTermRef]:
        # Read STUDY DESIGN DESCRIPTORS header
        line = self._read_next_line()
        if not line[0] == STUDY_DESIGN_DESCRIPTORS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_DESIGN_DESCRIPTORS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Study Design',
            STUDY_DESIGN_DESCR_KEYS,
            STUDY_DESIGN_DESCRIPTORS)
        # Create resulting objects
        columns = zip(*(section[k] for k in STUDY_DESIGN_DESCR_KEYS))
        for i, (type_term, type_term_acc, type_term_src) in enumerate(columns):
            otype = models.build_freetext_or_term_ref(
                type_term, type_term_acc, type_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.DesignDescriptorsInfo(otype, comments)

    def _read_study_publications(self) -> Iterator[models.PublicationInfo]:
        # Read STUDY PUBLICATIONS header
        line = self._read_next_line()
        if not line[0] == STUDY_PUBLICATIONS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_PUBLICATIONS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Study Pub',
            STUDY_PUBLICATIONS_KEYS,
            STUDY_PUBLICATIONS)
        # Create resulting objects
        columns = zip(*(section[k] for k in STUDY_PUBLICATIONS_KEYS))
        for i, (pubmed_id, doi, authors, title, status_term,
                status_term_acc, status_term_src) in enumerate(columns):
            status = models.build_freetext_or_term_ref(
                status_term, status_term_acc,
                status_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.PublicationInfo(
                pubmed_id, doi, authors, title, status, comments)

    def _read_study_factors(self) -> Iterator[models.FactorInfo]:
        # Read STUDY FACTORS header
        line = self._read_next_line()
        if not line[0] == STUDY_FACTORS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_FACTORS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Study Factor',
            STUDY_FACTORS_KEYS,
            STUDY_FACTORS)
        # Create resulting objects
        columns = zip(*(section[k] for k in STUDY_FACTORS_KEYS))
        for i, (name, type_term, type_term_acc,
                type_term_src) in enumerate(columns):
            otype = models.build_freetext_or_term_ref(
                type_term, type_term_acc, type_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.FactorInfo(name, otype, comments)

    def _read_study_assays(self) -> Iterator[models.AssayInfo]:
        # Read STUDY ASSAYS header
        line = self._read_next_line()
        if not line[0] == STUDY_ASSAYS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_ASSAYS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Study Assay', STUDY_ASSAYS_KEYS, STUDY_ASSAYS)
        # Create resulting objects
        columns = zip(*(section[k] for k in STUDY_ASSAYS_KEYS))
        for i, (file_, meas_type, meas_type_term_acc, meas_type_term_src,
                tech_type, tech_type_term_acc, tech_type_term_src, tech_plat) \
                in enumerate(columns):
            if not file_:  # don't allow incomplete assay columns
                tpl = 'Expected "a_*.txt" in line {}; found: "{}"'
                msg = tpl.format(STUDY_ASSAY_FILE_NAME, file_)
                raise ParseIsatabException(msg)
            meas = models.build_freetext_or_term_ref(
                meas_type, meas_type_term_acc,
                meas_type_term_src, self._ontology_refs)
            tech = models.build_freetext_or_term_ref(
                tech_type, tech_type_term_acc,
                tech_type_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.AssayInfo(
                meas, tech, tech_plat, Path(file_), comments)

    def _read_study_protocols(self) -> Iterator[models.ProtocolInfo]:
        # Read STUDY PROTOCOLS header
        line = self._read_next_line()
        if not line[0] == STUDY_PROTOCOLS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_PROTOCOLS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Study Protocol', STUDY_PROTOCOLS_KEYS, STUDY_PROTOCOLS)
        # Create resulting objects
        columns = zip(*(section[k] for k in STUDY_PROTOCOLS_KEYS))
        for i, (name, type_term, type_term_acc, type_term_src, description,
                uri, version, para_names, para_name_term_accs,
                para_name_term_srcs, comp_names, comp_types,
                comp_type_term_accs, comp_type_term_srcs) \
                in enumerate(columns):
            if not name:  # don't allow unnamed assay columns
                tpl = 'Expected protocol name in line {}; found: "{}"'
                msg = tpl.format(STUDY_PROTOCOL_NAME, name)
                raise ParseIsatabException(msg)
            type_ont = models.build_freetext_or_term_ref(
                type_term, type_term_acc, type_term_src, self._ontology_refs)
            paras = {p.name if hasattr(p, "name") else p: p
                     for p in _split_study_protocols_parameters(
                para_names, para_name_term_accs,
                para_name_term_srcs, self._ontology_refs)}
            comps = {c.name: c for c in _split_study_protocols_components(
                comp_names, comp_types, comp_type_term_accs,
                comp_type_term_srcs, self._ontology_refs)}
            comments = _parse_comments(section, comment_keys, i)
            yield models.ProtocolInfo(name, type_ont, description, uri,
                                      version, paras, comps, comments)

    def _read_study_contacts(self) -> Iterator[models.ContactInfo]:
        # Read STUDY CONTACTS header
        line = self._read_next_line()
        if not line[0] == STUDY_CONTACTS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_CONTACTS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            'Study Person',
            STUDY_CONTACTS_KEYS,
            STUDY_CONTACTS)
        # Create resulting objects
        columns = zip(
            *(section[k] for k in STUDY_CONTACTS_KEYS))
        for i, (last_name, first_name, mid_initial, email, phone, fax, address,
                affiliation, role_term, role_term_acc, role_term_src) in \
                enumerate(columns):
            role = models.build_freetext_or_term_ref(
                role_term, role_term_acc, role_term_src, self._ontology_refs)
            comments = _parse_comments(section, comment_keys, i)
            yield models.ContactInfo(
                last_name, first_name, mid_initial, email, phone, fax, address,
                affiliation, role, comments)

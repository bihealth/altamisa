# -*- coding: utf-8 -*-
"""Code for parsing investigation files.
"""

import os
import csv
from typing import Iterator, TextIO

from . import models
from ..exceptions import ParseIsatabException

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


# The string constants used for the references to ontology terms.

TERM_SOURCE_NAME = 'Term Source Name'
TERM_SOURCE_FILE = 'Term Source File'
TERM_SOURCE_VERSION = 'Term Source Version'
TERM_SOURCE_DESCRIPTION = 'Term Source Description'
ONTOLOGY_SOURCE_REF_KEYS = (
    TERM_SOURCE_NAME, TERM_SOURCE_FILE, TERM_SOURCE_VERSION,
    TERM_SOURCE_DESCRIPTION)


# The string constants used for the references to investigation basic info
INVESTIGATION_IDENTIFIER = 'Investigation Identifier'
INVESTIGATION_TITLE = 'Investigation Title'
INVESTIGATION_DESCRIPTION = 'Investigation Description'
INVESTIGATION_SUBMISSION_DATE = 'Investigation Submission Date'
INVESTIGATION_PUBLIC_RELEASE_DATE = 'Investigation Public Release Date'
INVESTIGATION_INFO_REF_KEYS = (
    INVESTIGATION_IDENTIFIER, INVESTIGATION_TITLE, INVESTIGATION_DESCRIPTION,
    INVESTIGATION_SUBMISSION_DATE, INVESTIGATION_PUBLIC_RELEASE_DATE)


# The string constants used for the references to studies basic info
STUDY_IDENTIFIER = 'Study Identifier'
STUDY_TITLE = 'Study Title'
STUDY_DESCRIPTION = 'Study Description'
STUDY_SUBMISSION_DATE = 'Study Submission Date'
STUDY_PUBLIC_RELEASE_DATE = 'Study Public Release Date'
STUDY_FILE_NAME = 'Study File Name'
STUDY_INFO_REF_KEYS = (
    STUDY_IDENTIFIER, STUDY_TITLE, STUDY_DESCRIPTION,
    STUDY_SUBMISSION_DATE, STUDY_PUBLIC_RELEASE_DATE, STUDY_FILE_NAME)


# The string constants used for the references to assays
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
STUDY_ASSAY_REF_KEYS = (
    STUDY_ASSAY_FILE_NAME,
    STUDY_ASSAY_MEASUREMENT_TYPE,
    STUDY_ASSAY_MEASUREMENT_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_ASSAY_MEASUREMENT_TYPE_TERM_SOURCE_REF,
    STUDY_ASSAY_TECHNOLOGY_TYPE,
    STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_ACCESSION_NUMBER,
    STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_SOURCE_REF,
    STUDY_ASSAY_TECHNOLOGY_PLATFORM
)


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

    def _read_next_line(self):
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        self._line = next(self._reader)
        while self._line is not None and (
                not self._line or self._line[0].startswith('#')):
            self._line = next(self._reader)
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
        ontology_ref = {
            o.name: o for o in self._read_ontology_source_reference()}
        info = self._read_basic_info()
        publications = list(self._read_publications())
        contacts = list(self._read_contacts())
        studies = list(self._read_studies())
        return models.InvestigationInfo(
            ontology_ref, info, publications, contacts, studies)

    # reader for content of sections with possibly multiple columns
    # i.e. ONTOLOGY SOURCE REFERENCE, INVESTIGATION PUBLICATIONS,
    # INVESTIGATION CONTACTS, STUDY DESIGN DESCRIPTORS, STUDY PUBLICATIONS,
    # STUDY FACTORS, STUDY ASSAYS, STUDY PROTOCOLS, STUDY CONTACTS
    def _read_multi_column_section(self, prefix, ref_keys, section_name):
        section = {}
        while (self._next_line_startswith(prefix) or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if line[0].startswith('Comment'):
                continue  # skip comments
            key = line[0]
            if key not in ref_keys:
                tpl = 'Line must start with one of {} but is {}'
                msg = tpl.format(ref_keys, line)
                raise ParseIsatabException(msg)
            if key in section:
                tpl = 'Key {} repeated, previous value {}'
                msg = tpl.format(key, section[key])
                raise ParseIsatabException(msg)
            section[key] = line[1:]
        # Check that all keys are given and all contain the same number of
        # entries
        if len(section) != len(ref_keys):
            tpl = 'Missing entries in section {}; found: {}'
            msg = tpl.format(section_name, list(sorted(section)))
            raise ParseIsatabException(msg)
        if not len(set([len(v) for v in section.values()])) == 1:
            tpl = 'Inconsistent entry lengths in section {}'
            msg = tpl.format(section_name)
            raise ParseIsatabException(msg)
        return section

    # reader for content of a section with only one column
    # i.e. INVESTIGATION and STUDY
    def _read_single_column_section(self, prefix, ref_keys, section_name):
        # Read the lines in this section.
        section = {}
        while (self._next_line_startswith(prefix) or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if line[0].startswith('Comment'):
                continue  # skip comments
            if len(line) > 2:
                tpl = 'Line {} contains more than one value: {}'
                msg = tpl.format(line[0], line[1:])
                raise ParseIsatabException(msg)
            key = line[0]
            if key not in ref_keys:
                tpl = 'Line must start with one of {} but is {}'
                msg = tpl.format(ref_keys, line)
                raise ParseIsatabException(msg)
            if key in section:
                tpl = 'Key {} repeated, previous value {}'
                msg = tpl.format(key, section[key])
                raise ParseIsatabException(msg)
            # read value if field is available, empty string else
            section[key] = line[1] if len(line) > 1 else ''
        # Check that all keys are given
        if len(section) != len(ref_keys):
            tpl = 'Missing entries in section {}; found: {}'
            msg = tpl.format(section_name, list(sorted(section)))
            raise ParseIsatabException(msg)
        return section

    def _read_ontology_source_reference(self) -> Iterator[
            models.OntologyRef]:
        # Read ONTOLOGY SOURCE REFERENCE header
        line = self._read_next_line()
        if not line[0] == ONTOLOGY_SOURCE_REFERENCE:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(ONTOLOGY_SOURCE_REFERENCE, line)
            raise ParseIsatabException(msg)
        # Read the other four lines in this section.
        section = self._read_multi_column_section(
            'Term Source', ONTOLOGY_SOURCE_REF_KEYS, ONTOLOGY_SOURCE_REFERENCE)
        # Create resulting objects
        columns = zip(*(section[k] for k in ONTOLOGY_SOURCE_REF_KEYS))
        for name, file_, version, desc in columns:
            # Check if ontology source is complete
            if not (name and file_ and version and desc):
                tpl = 'Incomplete ontology source; found: {}, {}, {}, {}'
                msg = tpl.format(name, file_, version, desc)
                raise ParseIsatabException(msg)
            yield models.OntologyRef(name, file_, version, desc)

    def _read_basic_info(self) -> models.BasicInfo:
        # Read INVESTIGATION header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section = self._read_single_column_section(
            'Investigation', INVESTIGATION_INFO_REF_KEYS, INVESTIGATION)
        # Create resulting object
        # TODO: do we really need the name of the investigation file?
        return models.BasicInfo(os.path.basename(self.input_file.name),
                                section[INVESTIGATION_IDENTIFIER],
                                section[INVESTIGATION_TITLE],
                                section[INVESTIGATION_DESCRIPTION],
                                section[INVESTIGATION_SUBMISSION_DATE],
                                section[INVESTIGATION_PUBLIC_RELEASE_DATE])

    def _read_publications(self) -> Iterator[models.PublicationInfo]:
        # Read INVESTIGATION PUBLICATIONS header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION_PUBLICATIONS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION_PUBLICATIONS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._next_line_startswith('Investigation Pub') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

    def _read_contacts(self) -> Iterator[models.ContactInfo]:
        # Read INVESTIGATION CONTACTS header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION_CONTACTS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION_CONTACTS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._next_line_startswith('Investigation Person') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

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
            section = self._read_single_column_section(
                'Study', STUDY_INFO_REF_KEYS, STUDY)
            # From this, parse the basic information from the study
            basic_info = models.BasicInfo(section[STUDY_FILE_NAME],
                                          section[STUDY_IDENTIFIER],
                                          section[STUDY_TITLE],
                                          section[STUDY_DESCRIPTION],
                                          section[STUDY_SUBMISSION_DATE],
                                          section[STUDY_PUBLIC_RELEASE_DATE])
            # Read the remaining sections for this study
            # TODO: specs says "order MAY vary"
            design_descriptors = list(self._read_study_design_descriptors())
            publications = list(self._read_study_publications())
            factors = {f.name: f for f in self._read_study_factors()}
            assays = {a.path: a for a in self._read_study_assays()}
            protocols = {p.name: p for p in self._read_study_protocols()}
            contacts = list(self._read_study_contacts())
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
        # section = {}
        while (self._next_line_startswith('Study Design') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

    def _read_study_publications(self) -> Iterator[models.PublicationInfo]:
        # Read STUDY PUBLICATIONS header
        line = self._read_next_line()
        if not line[0] == STUDY_PUBLICATIONS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_PUBLICATIONS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._next_line_startswith('Study Pub') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

    def _read_study_factors(self) -> Iterator[models.FactorInfo]:
        # Read STUDY FACTORS header
        line = self._read_next_line()
        if not line[0] == STUDY_FACTORS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_FACTORS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._next_line_startswith('Study Factor') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

    def _read_study_assays(self) -> Iterator[models.AssayInfo]:
        # Read STUDY ASSAYS header
        line = self._read_next_line()
        if not line[0] == STUDY_ASSAYS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_ASSAYS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section = self._read_multi_column_section(
            'Study Assay', STUDY_ASSAY_REF_KEYS, STUDY_ASSAYS)
        # Create resulting objects
        columns = zip(*(section[k] for k in STUDY_ASSAY_REF_KEYS))
        for file_, meas_type, meas_type_term_acc, meas_type_term_src, \
            tech_type, tech_type_term_acc, tech_type_term_src, tech_plat \
                in columns:
            if not file_:  # don't allow incomplete assay columns
                tpl = 'Expected "a_*.txt" in line {}; found: "{}"'
                msg = tpl.format(STUDY_ASSAY_FILE_NAME, file_)
                raise ParseIsatabException(msg)
            meas = models.OntologyTermRef(
                meas_type, tech_type_term_acc, meas_type_term_src)
            tech = models.OntologyTermRef(
                tech_type, tech_type_term_acc, tech_type_term_src)
            yield models.AssayInfo(meas, tech, tech_plat, file_)

    def _read_study_protocols(self) -> Iterator[models.ProtocolInfo]:
        # Read STUDY PROTOCOLS header
        line = self._read_next_line()
        if not line[0] == STUDY_PROTOCOLS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_PROTOCOLS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._next_line_startswith('Study Protocol') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

    def _read_study_contacts(self) -> Iterator[models.ContactInfo]:
        # Read STUDY CONTACTS header
        line = self._read_next_line()
        if not line[0] == STUDY_CONTACTS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_CONTACTS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._next_line_startswith('Study Person') or
               self._next_line_startswith_comment()):
            line = self._read_next_line()
            if self._next_line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

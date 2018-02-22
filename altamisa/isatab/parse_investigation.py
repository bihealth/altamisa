# -*- coding: utf-8 -*-
"""Code for parsing investigation files.
"""

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

    def _line_startswith_comment(self):
        if not self._line:
            return False
        else:
            return self._line[0].startswith('Comment')

    def _line_startswith(self, token):
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

    def _read_ontology_source_reference(self) -> Iterator[
            models.OntologyRef]:
        # Read ONTOLOGY SOURCE REFERENCE header
        line = self._read_next_line()
        if not line[0] == ONTOLOGY_SOURCE_REFERENCE:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(ONTOLOGY_SOURCE_REFERENCE, line)
            raise ParseIsatabException(msg)
        # Read the other four lines in this section.
        section = {}
        while (self._line_startswith('Term Source') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
                continue  # skip comments
            if line[0] not in ONTOLOGY_SOURCE_REF_KEYS:
                tpl = 'Line must start with one of {} but is {}'
                msg = tpl.format(ONTOLOGY_SOURCE_REF_KEYS, line)
                raise ParseIsatabException(msg)
            key = line[0]
            if key in section:
                tpl = 'Key {} repeated, previous value {}'
                msg = tpl.format(key, section[key])
                raise ParseIsatabException(msg)
            section[key] = line[1:]
        # Check that all four keys are given and all contain the same number
        # of entries
        if len(section) != 4:
            tpl = 'Missing entries in section {}; found: {}'
            msg = tpl.format(ONTOLOGY_SOURCE_REFERENCE, list(sorted(section)))
            raise ParseIsatabException(msg)
        if not len(set([len(v) for v in section.values()])) == 1:
            tpl = 'Inconsistent entry lengths in section {}'
            msg = tpl.format(ONTOLOGY_SOURCE_REFERENCE)
            raise ParseIsatabException(msg)
        # Create resulting objects
        columns = zip(*(section[k] for k in ONTOLOGY_SOURCE_REF_KEYS))
        for name, file_, version, desc in columns:
            yield models.OntologyRef(name, file_, version, desc)

    def _read_basic_info(self) -> models.BasicInfo:
        # Read INVESTIGATION header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._line_startswith('Investigation') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
                continue  # skip comments
            # XXX
        return models.BasicInfo('', '', '', '', '', '')

    def _read_publications(self) -> Iterator[models.PublicationInfo]:
        # Read INVESTIGATION PUBLICATIONS header
        line = self._read_next_line()
        if not line[0] == INVESTIGATION_PUBLICATIONS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(INVESTIGATION_PUBLICATIONS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._line_startswith('Investigation Pub') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
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
        while (self._line_startswith('Investigation Person') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
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
            # section = {}
            while (self._line_startswith('Study') or
                   self._line_startswith_comment()):
                line = self._read_next_line()
                if self._line_startswith_comment():
                    continue  # skip comments
                # XXX
            # From this, parse the basic information from the study
            basic_info = models.BasicInfo('', '', '', '', '', '')
            design_descriptors = list(self._read_study_design_descriptors())
            publications = list(self._read_study_publications())
            factors = {f.name: f for f in self._read_study_factors()}
            assays = {a.name: a for a in self._read_study_assays()}
            protocols = {p.name: p for p in self._read_study_protocols()}
            contacts = list(self._read_study_contacts())
            # Read the remaining sections for this study
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
        while (self._line_startswith('Study Design') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
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
        while (self._line_startswith('Study Pub') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
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
        while (self._line_startswith('Study Factor') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
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
        # section = {}
        while (self._line_startswith('Study Assay') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

    def _read_study_protocols(self) -> Iterator[models.ProtocolInfo]:
        # Read STUDY PROTOCOLS header
        line = self._read_next_line()
        if not line[0] == STUDY_PROTOCOLS:
            tpl = 'Expected {} but got {}'
            msg = tpl.format(STUDY_PROTOCOLS, line)
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        # section = {}
        while (self._line_startswith('Study Protocol') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
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
        while (self._line_startswith('Study Person') or
               self._line_startswith_comment()):
            line = self._read_next_line()
            if self._line_startswith_comment():
                continue  # skip comments
                yield None  # XXX

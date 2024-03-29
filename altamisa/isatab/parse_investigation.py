# -*- coding: utf-8 -*-
"""Code for parsing investigation files.
"""

from __future__ import generator_stop

import csv
import datetime
import os
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, TextIO
import warnings

from . import models
from ..constants import investigation_headers
from ..exceptions import ParseIsatabException, ParseIsatabWarning
from .helpers import list_strip

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bih-charite.de>"


# Helper function to extract comment headers and values from a section dict
def _parse_comments(section, comment_keys, i=None):
    def _parse_comment_header(val):
        # key might start with "Comment[" but NOT "Comment ["
        tok = val[len("Comment") :]
        if not tok or tok[0] != "[" or tok[-1] != "]":  # pragma: no cover
            msg = f'Problem parsing comment header "{val}"'
            raise ParseIsatabException(msg)
        return tok[1:-1]

    if i is not None:
        comments = tuple(
            models.Comment(_parse_comment_header(k), section[k][i]) for k in comment_keys
        )
    else:
        comments = tuple(models.Comment(_parse_comment_header(k), section[k]) for k in comment_keys)

    return comments


# Helper function to extract protocol parameters
def _split_study_protocols_parameters(
    protocol_name: str, names_str: str, name_term_accs_str: str, name_term_srcs_str: str
) -> Iterator[models.FreeTextOrTermRef]:
    names = names_str.split(";")
    name_term_accs = name_term_accs_str.split(";")
    name_term_srcs = name_term_srcs_str.split(";")
    if not (len(names) == len(name_term_accs) == len(name_term_srcs)):  # pragma: no cover
        msg = (
            f"Unequal parameter splits in protocol '{protocol_name}':\n"
            f"Parameter Names: {len(names)}\n"
            f"Term Accession Numers: {len(name_term_accs)}\n"
            f"Term Source REFs: {len(name_term_srcs)}"
        )
        raise ParseIsatabException(msg)
    if len(names) > len(set(names)):  # pragma: no cover
        msg = f"Repeated protocol parameter; found: {names}"
        raise ParseIsatabException(msg)
    for name, acc, src in zip(names, name_term_accs, name_term_srcs):
        if any((name, acc, src)):  # skips empty parameters
            yield models.OntologyTermRef(name, acc, src)


# Helper function to extract protocol components
def _split_study_protocols_components(
    protocol_name: str,
    names_str: str,
    types_str: str,
    type_term_accs_str: str,
    type_term_srcs_str: str,
) -> Iterator[models.ProtocolComponentInfo]:
    names = names_str.split(";")
    types = types_str.split(";")
    type_term_accs = type_term_accs_str.split(";")
    type_term_srcs = type_term_srcs_str.split(";")
    if not (
        len(names) == len(types) == len(type_term_accs) == len(type_term_srcs)
    ):  # pragma: no cover
        msg = (
            f"Unequal component splits in protocol '{protocol_name}':\n"
            f"Components Names: {len(names)}\n"
            f"Components Types: {len(types)}\n"
            f"Type Term Accession Numers: {len(type_term_accs)}\n"
            f"Type Term Source REFs: {len(type_term_srcs)}"
        )
        raise ParseIsatabException(msg)
    if len(names) > len(set(names)):  # pragma: no cover
        msg = f"Repeated protocol components; found: {names}"
        raise ParseIsatabException(msg)
    for name, ctype, acc, src in zip(
        names, types, type_term_accs, type_term_srcs
    ):  # pragma: no cover
        if not name and any((ctype, acc, src)):
            msg = f'Missing protocol component name; found: "{name}", "{ctype}", "{acc}", "{src}"'
            raise ParseIsatabException(msg)
        if any((name, ctype, acc, src)):  # skips empty components
            yield models.ProtocolComponentInfo(name, models.OntologyTermRef(ctype, acc, src))


# Helper function to validate and convert string dates to date objects
def _parse_date(date_string: str) -> Optional[datetime.date]:
    if date_string:
        try:
            return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError as e:  # pragma: no cover
            raise ParseIsatabException(f'Invalid ISO8601 date "{date_string}"') from e
    else:
        return None


class InvestigationReader:
    """
    Main class to read an investigation file into an ``InvestigationInfo`` object.

    :type input_file: TextIO
    :param input_file: ISA-Tab investigation file
    """

    @classmethod
    def from_stream(cls, input_file: TextIO, filename=None):
        """Construct from file-like object"""
        return InvestigationReader(input_file, filename)

    def __init__(self, input_file: TextIO, filename=None):
        self._filename = filename or getattr(input_file, "name", "<no file>")
        self._reader = csv.reader(input_file, delimiter="\t", quotechar='"')
        self._line: Optional[List[str]] = None
        self._read_next_line()

    def _read_next_line(self) -> Optional[List[str]]:
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        try:
            self._line = list_strip(next(self._reader))
            while self._line is not None and (not self._line or self._line[0].startswith("#")):
                self._line = list_strip(next(self._reader))
        except StopIteration:
            self._line = None
        except UnicodeDecodeError as e:  # pragma: no cover
            msg = f"Invalid encoding of investigation file '{self._filename}' (use Unicode/UTF-8)."
            raise ParseIsatabException(msg) from e
        return prev_line

    def _next_line_startswith_comment(self):
        if not self._line:
            return False
        else:
            return self._line[0].startswith("Comment")

    def _next_line_startswith(self, token):
        """Return whether line starts with ``token``"""
        if not self._line:
            return False
        else:
            return self._line[0].startswith(token)

    def read(self) -> models.InvestigationInfo:
        """
        Read the investigation file

        :rtype: models.InvestigationInfo
        :returns: Investigation model including all information from the investigation file
        """
        # Read sections in fixed order
        # ("section headings MUST appear in the Investigation file (in order)")
        ontology_refs = {o.name: o for o in self._read_ontology_source_reference()}
        info = self._read_basic_info()
        publications = tuple(self._read_publications())
        contacts = tuple(self._read_contacts())
        studies = tuple(self._read_studies())
        investigation = models.InvestigationInfo(
            ontology_refs, info, publications, contacts, studies
        )
        return investigation

    # reader for content of sections with possibly multiple columns
    # i.e. ONTOLOGY SOURCE REFERENCE, INVESTIGATION PUBLICATIONS,
    # INVESTIGATION CONTACTS, STUDY DESIGN DESCRIPTORS, STUDY PUBLICATIONS,
    # STUDY FACTORS, STUDY ASSAYS, STUDY PROTOCOLS, STUDY CONTACTS
    def _read_multi_column_section(self, prefix: str, ref_keys: Sequence[str], section_name: str):
        section = {}
        comment_keys = []
        while self._next_line_startswith(prefix) or self._next_line_startswith_comment():
            line = self._read_next_line()
            assert line is not None
            key = line[0]
            if key.startswith("Comment"):
                comment_keys.append(key)
            elif key not in ref_keys:  # pragma: no cover
                msg = f"Line must start with one of {ref_keys} but is {line}"
                raise ParseIsatabException(msg)
            if key in section:  # pragma: no cover
                msg = f'Key {key} repeated, previous value "{section[key]}"'
                raise ParseIsatabException(msg)
            section[key] = line[1:]
        # Check that all keys are given and all contain the same number of entries
        if len(section) != len(ref_keys) + len(comment_keys):  # pragma: no cover
            msg = f"Missing entries in section {section_name}; only found: {list(sorted(section))}"
            raise ParseIsatabException(msg)  # TODO: should be warning?
        if not len(set([len(v) for v in section.values()])) == 1:  # pragma: no cover
            lengths = "\n".join(
                map(str, [f"{key}: {len(value)}" for key, value in section.items()])
            )
            msg = f"Inconsistent entry lengths in section {section_name}:\n{lengths}"
            raise ParseIsatabException(msg)
        return section, comment_keys

    # reader for content of a section with only one column
    # i.e. INVESTIGATION and STUDY
    def _read_single_column_section(self, prefix, ref_keys, section_name):
        # Read the lines in this section.
        section = {}
        comment_keys = []
        while self._next_line_startswith(prefix) or self._next_line_startswith_comment():
            line = self._read_next_line()
            if line is None:
                break
            if len(line) > 2:  # pragma: no cover
                msg = f"Line {line[0]} contains more than one value: {line[1:]}"
                raise ParseIsatabException(msg)
            key = line[0]
            if key.startswith("Comment"):
                comment_keys.append(key)
            elif key not in ref_keys:  # pragma: no cover
                msg = f"Line must start with one of {ref_keys} but is {line}"
                raise ParseIsatabException(msg)
            if key in section:  # pragma: no cover
                msg = f'Key {key} repeated, previous value "{section[key]}"'
                raise ParseIsatabException(msg)
            # read value if field is available, empty string else
            section[key] = line[1] if len(line) > 1 else ""
        # Check that all keys are given
        if len(section) != len(ref_keys) + len(comment_keys):  # pragma: no cover
            msg = f"Missing entries in section {section_name}; only found: {list(sorted(section))}"
            raise ParseIsatabException(msg)  # TODO: should be warning?
        return section, comment_keys

    def _read_ontology_source_reference(self) -> Iterator[models.OntologyRef]:
        # Read ONTOLOGY SOURCE REFERENCE header
        line = self._read_next_line()
        if (
            not line or not line[0] == investigation_headers.ONTOLOGY_SOURCE_REFERENCE
        ):  # pragma: no cover
            msg = f"Expected {investigation_headers.ONTOLOGY_SOURCE_REFERENCE} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other four lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Term Source",
            investigation_headers.ONTOLOGY_SOURCE_REF_KEYS,
            investigation_headers.ONTOLOGY_SOURCE_REFERENCE,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.ONTOLOGY_SOURCE_REF_KEYS))
        for i, (name, file_, version, desc) in enumerate(columns):
            comments = _parse_comments(section, comment_keys, i)
            # If ontology source is empty, skip it
            # (since ISAcreator always adds a last empty ontology column)
            if not any((name, file_, version, desc, any(comments))):
                msg = f"Skipping empty ontology source: {name}, {file_}, {version}, {desc}"
                warnings.warn(msg, ParseIsatabWarning)
                continue
            yield models.OntologyRef(name, file_, version, desc, comments, list(section.keys()))

    def _read_basic_info(self) -> models.BasicInfo:
        # Read INVESTIGATION header
        line = self._read_next_line()
        if not line or not line[0] == investigation_headers.INVESTIGATION:  # pragma: no cover
            msg = f"Expected {investigation_headers.INVESTIGATION} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_single_column_section(
            "Investigation",
            investigation_headers.INVESTIGATION_INFO_KEYS,
            investigation_headers.INVESTIGATION,
        )
        # Create resulting object
        # TODO: do we really need the name of the investigation file?
        comments = _parse_comments(section, comment_keys)
        return models.BasicInfo(
            Path(os.path.basename(self._filename)),
            section[investigation_headers.INVESTIGATION_IDENTIFIER],
            section[investigation_headers.INVESTIGATION_TITLE],
            section[investigation_headers.INVESTIGATION_DESCRIPTION],
            _parse_date(section[investigation_headers.INVESTIGATION_SUBMISSION_DATE]),
            _parse_date(section[investigation_headers.INVESTIGATION_PUBLIC_RELEASE_DATE]),
            comments,
            list(section.keys()),
        )

    def _read_publications(self) -> Iterator[models.PublicationInfo]:
        # Read INVESTIGATION PUBLICATIONS header
        line = self._read_next_line()
        if (
            not line or not line[0] == investigation_headers.INVESTIGATION_PUBLICATIONS
        ):  # pragma: no cover
            msg = f"Expected {investigation_headers.INVESTIGATION_PUBLICATIONS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Investigation Pub",
            investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS,
            investigation_headers.INVESTIGATION_PUBLICATIONS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS))
        for (
            i,
            (pubmed_id, doi, authors, title, status_term, status_term_acc, status_term_src),
        ) in enumerate(columns):
            status = models.OntologyTermRef(status_term, status_term_acc, status_term_src)
            comments = _parse_comments(section, comment_keys, i)
            yield models.PublicationInfo(
                pubmed_id, doi, authors, title, status, comments, list(section.keys())
            )

    def _read_contacts(self) -> Iterator[models.ContactInfo]:
        # Read INVESTIGATION CONTACTS header
        line = self._read_next_line()
        if (
            not line or not line[0] == investigation_headers.INVESTIGATION_CONTACTS
        ):  # pragma: no cover
            msg = f"Expected {investigation_headers.INVESTIGATION_CONTACTS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Investigation Person",
            investigation_headers.INVESTIGATION_CONTACTS_KEYS,
            investigation_headers.INVESTIGATION_CONTACTS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.INVESTIGATION_CONTACTS_KEYS))
        for (
            i,
            (
                last_name,
                first_name,
                mid_initial,
                email,
                phone,
                fax,
                address,
                affiliation,
                role_term,
                role_term_acc,
                role_term_src,
            ),
        ) in enumerate(columns):
            role = models.OntologyTermRef(role_term, role_term_acc, role_term_src)
            comments = _parse_comments(section, comment_keys, i)
            yield models.ContactInfo(
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
                list(section.keys()),
            )

    def _read_studies(self) -> Iterator[models.StudyInfo]:
        while self._line:
            # Read STUDY header
            line = self._read_next_line()
            if not line or not line[0] == investigation_headers.STUDY:  # pragma: no cover
                msg = f"Expected {investigation_headers.STUDY} but got {line}"
                raise ParseIsatabException(msg)
            # Read the other lines in this section.
            section, comment_keys = self._read_single_column_section(
                "Study", investigation_headers.STUDY_INFO_KEYS, investigation_headers.STUDY
            )
            # From this, parse the basic information from the study
            comments = _parse_comments(section, comment_keys)
            basic_info = models.BasicInfo(
                (
                    Path(section[investigation_headers.STUDY_FILE_NAME])
                    if section[investigation_headers.STUDY_FILE_NAME]
                    else None
                ),
                section[investigation_headers.STUDY_IDENTIFIER],
                section[investigation_headers.STUDY_TITLE],
                section[investigation_headers.STUDY_DESCRIPTION],
                _parse_date(section[investigation_headers.STUDY_SUBMISSION_DATE]),
                _parse_date(section[investigation_headers.STUDY_PUBLIC_RELEASE_DATE]),
                comments,
                list(section.keys()),
            )
            # Read the remaining sections for this study in fixed order
            # (though the study specification says the "order MAY vary", the overall investigation
            # specification demands that "section headings MUST appear in the Investigation file
            # (in order)", which we perceive as higher priority.)
            design_descriptors = tuple(self._read_study_design_descriptors())
            publications = tuple(self._read_study_publications())
            factors = {f.name: f for f in self._read_study_factors()}
            assays = tuple(self._read_study_assays())
            protocols = {p.name: p for p in self._read_study_protocols()}
            contacts = tuple(self._read_study_contacts())
            # Create study object
            yield models.StudyInfo(
                basic_info, design_descriptors, publications, factors, assays, protocols, contacts
            )

    def _read_study_design_descriptors(self) -> Iterator[models.DesignDescriptorsInfo]:
        # Read STUDY DESIGN DESCRIPTORS header
        line = self._read_next_line()
        if (
            not line or not line[0] == investigation_headers.STUDY_DESIGN_DESCRIPTORS
        ):  # pragma: no cover
            msg = f"Expected {investigation_headers.STUDY_DESIGN_DESCRIPTORS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Study Design",
            investigation_headers.STUDY_DESIGN_DESCR_KEYS,
            investigation_headers.STUDY_DESIGN_DESCRIPTORS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.STUDY_DESIGN_DESCR_KEYS))
        for i, (type_term, type_term_acc, type_term_src) in enumerate(columns):
            otype = models.OntologyTermRef(type_term, type_term_acc, type_term_src)
            comments = _parse_comments(section, comment_keys, i)
            yield models.DesignDescriptorsInfo(otype, comments, list(section.keys()))

    def _read_study_publications(self) -> Iterator[models.PublicationInfo]:
        # Read STUDY PUBLICATIONS header
        line = self._read_next_line()
        if not line or not line[0] == investigation_headers.STUDY_PUBLICATIONS:  # pragma: no cover
            msg = f"Expected {investigation_headers.STUDY_PUBLICATIONS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Study Pub",
            investigation_headers.STUDY_PUBLICATIONS_KEYS,
            investigation_headers.STUDY_PUBLICATIONS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.STUDY_PUBLICATIONS_KEYS))
        for (
            i,
            (pubmed_id, doi, authors, title, status_term, status_term_acc, status_term_src),
        ) in enumerate(columns):
            status = models.OntologyTermRef(status_term, status_term_acc, status_term_src)
            comments = _parse_comments(section, comment_keys, i)
            yield models.PublicationInfo(
                pubmed_id, doi, authors, title, status, comments, list(section.keys())
            )

    def _read_study_factors(self) -> Iterator[models.FactorInfo]:
        # Read STUDY FACTORS header
        line = self._read_next_line()
        if not line or not line[0] == investigation_headers.STUDY_FACTORS:  # pragma: no cover
            msg = f"Expected {investigation_headers.STUDY_FACTORS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Study Factor",
            investigation_headers.STUDY_FACTORS_KEYS,
            investigation_headers.STUDY_FACTORS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.STUDY_FACTORS_KEYS))
        for i, (name, type_term, type_term_acc, type_term_src) in enumerate(columns):
            otype = models.OntologyTermRef(type_term, type_term_acc, type_term_src)
            comments = _parse_comments(section, comment_keys, i)
            yield models.FactorInfo(name, otype, comments, list(section.keys()))

    def _read_study_assays(self) -> Iterator[models.AssayInfo]:
        # Read STUDY ASSAYS header
        line = self._read_next_line()
        if not line or not line[0] == investigation_headers.STUDY_ASSAYS:  # pragma: no cover
            msg = f"Expected {investigation_headers.STUDY_ASSAYS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Study Assay",
            investigation_headers.STUDY_ASSAYS_KEYS,
            investigation_headers.STUDY_ASSAYS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.STUDY_ASSAYS_KEYS))
        for (
            i,
            (
                file_,
                meas_type,
                meas_type_term_acc,
                meas_type_term_src,
                tech_type,
                tech_type_term_acc,
                tech_type_term_src,
                tech_plat,
            ),
        ) in enumerate(columns):
            if any(
                (
                    file_,
                    meas_type,
                    meas_type_term_acc,
                    meas_type_term_src,
                    tech_type,
                    tech_type_term_acc,
                    tech_type_term_src,
                    tech_plat,
                )
            ):
                meas = models.OntologyTermRef(meas_type, meas_type_term_acc, meas_type_term_src)
                tech = models.OntologyTermRef(tech_type, tech_type_term_acc, tech_type_term_src)
                comments = _parse_comments(section, comment_keys, i)
                yield models.AssayInfo(
                    meas,
                    tech,
                    tech_plat,
                    Path(file_) if file_ else None,
                    comments,
                    list(section.keys()),
                )
            # else, i.e. if all assay fields are empty --> Nothing

    def _read_study_protocols(self) -> Iterator[models.ProtocolInfo]:
        # Read STUDY PROTOCOLS header
        line = self._read_next_line()
        if not line or not line[0] == investigation_headers.STUDY_PROTOCOLS:  # pragma: no cover
            msg = f"Expected {investigation_headers.STUDY_PROTOCOLS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Study Protocol",
            investigation_headers.STUDY_PROTOCOLS_KEYS,
            investigation_headers.STUDY_PROTOCOLS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.STUDY_PROTOCOLS_KEYS))
        for (
            i,
            (
                name,
                type_term,
                type_term_acc,
                type_term_src,
                description,
                uri,
                version,
                para_names,
                para_name_term_accs,
                para_name_term_srcs,
                comp_names,
                comp_types,
                comp_type_term_accs,
                comp_type_term_srcs,
            ),
        ) in enumerate(columns):
            if not name:  # don't allow unnamed protocol columns  # pragma: no cover
                tpl = 'Expected protocol name in line {}; found: "{}"'
                msg = tpl.format(investigation_headers.STUDY_PROTOCOL_NAME, name)
                raise ParseIsatabException(msg)
            type_ont = models.OntologyTermRef(type_term, type_term_acc, type_term_src)
            paras: Dict[str, models.FreeTextOrTermRef] = {}
            for p in _split_study_protocols_parameters(
                name, para_names, para_name_term_accs, para_name_term_srcs
            ):
                key = models.free_text_or_term_ref_to_str(p)
                if key:
                    paras[key] = p
            comps = {
                c.name: c
                for c in _split_study_protocols_components(
                    name, comp_names, comp_types, comp_type_term_accs, comp_type_term_srcs
                )
            }
            comments = _parse_comments(section, comment_keys, i)
            yield models.ProtocolInfo(
                name,
                type_ont,
                description,
                uri,
                version,
                paras,
                comps,
                comments,
                list(section.keys()),
            )

    def _read_study_contacts(self) -> Iterator[models.ContactInfo]:
        # Read STUDY CONTACTS header
        line = self._read_next_line()
        if not line or not line[0] == investigation_headers.STUDY_CONTACTS:  # pragma: no cover
            msg = f"Expected {investigation_headers.STUDY_CONTACTS} but got {line}"
            raise ParseIsatabException(msg)
        # Read the other lines in this section.
        section, comment_keys = self._read_multi_column_section(
            "Study Person",
            investigation_headers.STUDY_CONTACTS_KEYS,
            investigation_headers.STUDY_CONTACTS,
        )
        # Create resulting objects
        columns = zip(*(section[k] for k in investigation_headers.STUDY_CONTACTS_KEYS))
        for (
            i,
            (
                last_name,
                first_name,
                mid_initial,
                email,
                phone,
                fax,
                address,
                affiliation,
                role_term,
                role_term_acc,
                role_term_src,
            ),
        ) in enumerate(columns):
            role = models.OntologyTermRef(role_term, role_term_acc, role_term_src)
            comments = _parse_comments(section, comment_keys, i)
            yield models.ContactInfo(
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
                list(section.keys()),
            )

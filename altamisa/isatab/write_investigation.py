# -*- coding: utf-8 -*-
"""Code for parsing investigation files.
"""

from __future__ import generator_stop
import csv
import os
from typing import Dict, List, TextIO
import warnings

from ..exceptions import WriteIsatabException, WriteIsatabWarning
from ..constants import investigation_headers
from . import models


__author__ = (
    "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>, "
    "Mathias Kuhring <mathias.kuhring@bihealth.de>"
)


# Helper to extract comments and align them into rows
def _extract_comments(section_objects: list):
    names = sorted({comment.name for obj in section_objects for comment in obj.comments})
    comments = {name: [""] * len(section_objects) for name in names}
    for i, obj in enumerate(section_objects):
        for comment in obj.comments:
            comments[comment.name][i] = comment.value
    return comments


# Helper to extract a section header
def _extract_section_header(first_entry, section_name):
    """
    Extract reference header from first entry (column) in a section, assuming all entries have
    the same header resp. same corresponding values available.
    """
    if first_entry and first_entry.headers:
        # TODO: check that headers and attributes match
        return first_entry.headers
    else:
        tpl = "No reference headers available for section {}. Applying default order."
        msg = tpl.format(section_name)
        warnings.warn(msg, WriteIsatabWarning)
        return None


# Helper to create a dict with keys to empty lists
def _init_multi_column_section(section_keys) -> dict:
    return {key: list() for key in section_keys}


class InvestigationWriter:
    """Helper class that writes an investigation file from an ``InvestigationInfo`` object.
    """

    @classmethod
    def from_stream(
        cls,
        investigation: models.InvestigationInfo,
        output_file: TextIO,
        quote=None,
        lineterminator=None,
    ):
        """"""
        return InvestigationWriter(investigation, output_file, quote, lineterminator)

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        output_file: TextIO,
        quote=None,
        lineterminator=None,
    ):
        #: Investigation model
        self.investigation = investigation
        #: Investigation output file
        self.output_file = output_file
        #: Quote for csv export
        self.quote = quote
        #: Csv file writer
        self._writer = csv.writer(
            output_file,
            delimiter="\t",
            lineterminator=lineterminator or os.linesep,
            quoting=csv.QUOTE_NONE,
            # Can't use no quoting without escaping, so use different dummy quote here
            escapechar="\\",
            quotechar="|",
        )

    def write(self):
        """Write investigation file"""
        self._write_ontology_source_reference()
        self._write_basic_info()
        self._write_publications()
        self._write_contacts()
        self._write_studies()

    def _write_line(self, header, values):
        # Write an investigation line with header and values (potentially quoted)
        if self.quote:
            tpl = "".join((self.quote, "{}", self.quote))
            values = [tpl.format(v) for v in values]
        self._writer.writerow((header, *values))

    # Writer for headers and content of sections
    def _write_section(
        self,
        section_name: str,
        section: Dict[str, list],
        comments: Dict[str, list],
        headers: List[str] = None,
    ):
        # Add comments to section dict
        if comments:
            for key, value in comments.items():
                section["Comment[{}]".format(key)] = value
        # Write the section name
        self._writer.writerow((section_name,))
        # Write the lines in this section.
        if headers:
            # Use header order
            self._write_section_by_header_order(headers, section, section_name)
        else:
            # Use dict order
            for header, values in section.items():
                self._write_line(header, values)

    def _write_section_by_header_order(self, headers, section, section_name):
        # Write section based on header order
        for header in headers:
            if header in section:
                values = section.pop(header)
                self._write_line(header, values)
            else:
                tpl = "No data found for header {} in section {}"
                msg = tpl.format(header, section_name)
                raise WriteIsatabException(msg)
        if len(section) > 0:
            tpl = "Leftover rows found in section {}:\n{}"
            msg = tpl.format(section_name, section)
            raise WriteIsatabException(msg)

    def _write_ontology_source_reference(self):
        # Write ONTOLOGY SOURCE REFERENCE section
        section = _init_multi_column_section(investigation_headers.ONTOLOGY_SOURCE_REF_KEYS)
        for ontology_ref in self.investigation.ontology_source_refs.values():
            section[investigation_headers.TERM_SOURCE_NAME].append(ontology_ref.name)
            section[investigation_headers.TERM_SOURCE_FILE].append(ontology_ref.file)
            section[investigation_headers.TERM_SOURCE_VERSION].append(ontology_ref.version)
            section[investigation_headers.TERM_SOURCE_DESCRIPTION].append(ontology_ref.description)
        comments = _extract_comments(self.investigation.ontology_source_refs.values())
        headers = _extract_section_header(
            list(self.investigation.ontology_source_refs.values())[0]
            if self.investigation.ontology_source_refs
            else None,
            investigation_headers.ONTOLOGY_SOURCE_REFERENCE,
        )
        self._write_section(
            investigation_headers.ONTOLOGY_SOURCE_REFERENCE, section, comments, headers
        )

    def _write_basic_info(self):
        # Write INVESTIGATION section
        basic_info = self.investigation.info
        section = {
            investigation_headers.INVESTIGATION_IDENTIFIER: [basic_info.identifier],
            investigation_headers.INVESTIGATION_TITLE: [basic_info.title],
            investigation_headers.INVESTIGATION_DESCRIPTION: [basic_info.description],
            investigation_headers.INVESTIGATION_SUBMISSION_DATE: [basic_info.submission_date],
            investigation_headers.INVESTIGATION_PUBLIC_RELEASE_DATE: [
                basic_info.public_release_date
            ],
        }
        comments = _extract_comments([basic_info])
        headers = _extract_section_header(
            self.investigation.info, investigation_headers.INVESTIGATION
        )
        self._write_section(investigation_headers.INVESTIGATION, section, comments, headers)

    def _write_publications(self):
        # Write INVESTIGATION PUBLICATIONS section
        section = _init_multi_column_section(investigation_headers.INVESTIGATION_PUBLICATIONS_KEYS)
        for publication in self.investigation.publications:
            section[investigation_headers.INVESTIGATION_PUBMED_ID].append(publication.pubmed_id)
            section[investigation_headers.INVESTIGATION_PUBLICATION_DOI].append(publication.doi)
            section[investigation_headers.INVESTIGATION_PUBLICATION_AUTHOR_LIST].append(
                publication.authors
            )
            section[investigation_headers.INVESTIGATION_PUBLICATION_TITLE].append(publication.title)
            if (
                hasattr(publication.status, "name")
                and hasattr(publication.status, "accession")
                and hasattr(publication.status, "ontology_name")
            ):
                section[investigation_headers.INVESTIGATION_PUBLICATION_STATUS].append(
                    publication.status.name or ""
                )
                section[
                    investigation_headers.INVESTIGATION_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER
                ].append(publication.status.accession or "")
                section[
                    investigation_headers.INVESTIGATION_PUBLICATION_STATUS_TERM_SOURCE_REF
                ].append(publication.status.ontology_name or "")
            else:
                section[investigation_headers.INVESTIGATION_PUBLICATION_STATUS].append(
                    publication.status
                )
                section[
                    investigation_headers.INVESTIGATION_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER
                ].append("")
                section[
                    investigation_headers.INVESTIGATION_PUBLICATION_STATUS_TERM_SOURCE_REF
                ].append("")
        comments = _extract_comments(self.investigation.publications)
        headers = _extract_section_header(
            list(self.investigation.publications)[0] if self.investigation.publications else None,
            investigation_headers.INVESTIGATION_PUBLICATIONS,
        )
        self._write_section(
            investigation_headers.INVESTIGATION_PUBLICATIONS, section, comments, headers
        )

    def _write_contacts(self):
        # Write INVESTIGATION CONTACTS section
        section = _init_multi_column_section(investigation_headers.INVESTIGATION_CONTACTS_KEYS)
        for contact in self.investigation.contacts:
            section[investigation_headers.INVESTIGATION_PERSON_LAST_NAME].append(contact.last_name)
            section[investigation_headers.INVESTIGATION_PERSON_FIRST_NAME].append(
                contact.first_name
            )
            section[investigation_headers.INVESTIGATION_PERSON_MID_INITIALS].append(
                contact.mid_initial
            )
            section[investigation_headers.INVESTIGATION_PERSON_EMAIL].append(contact.email)
            section[investigation_headers.INVESTIGATION_PERSON_PHONE].append(contact.phone)
            section[investigation_headers.INVESTIGATION_PERSON_FAX].append(contact.fax)
            section[investigation_headers.INVESTIGATION_PERSON_ADDRESS].append(contact.address)
            section[investigation_headers.INVESTIGATION_PERSON_AFFILIATION].append(
                contact.affiliation
            )
            if (
                hasattr(contact.role, "name")
                and hasattr(contact.role, "accession")
                and hasattr(contact.role, "ontology_name")
            ):
                section[investigation_headers.INVESTIGATION_PERSON_ROLES].append(
                    contact.role.name or ""
                )
                section[
                    investigation_headers.INVESTIGATION_PERSON_ROLES_TERM_ACCESSION_NUMBER
                ].append(contact.role.accession or "")
                section[investigation_headers.INVESTIGATION_PERSON_ROLES_TERM_SOURCE_REF].append(
                    contact.role.ontology_name or ""
                )
            else:
                section[investigation_headers.INVESTIGATION_PERSON_ROLES].append(contact.role)
                section[
                    investigation_headers.INVESTIGATION_PERSON_ROLES_TERM_ACCESSION_NUMBER
                ].append("")
                section[investigation_headers.INVESTIGATION_PERSON_ROLES_TERM_SOURCE_REF].append("")
        comments = _extract_comments(self.investigation.contacts)
        headers = _extract_section_header(
            list(self.investigation.contacts)[0] if self.investigation.contacts else None,
            investigation_headers.INVESTIGATION_CONTACTS,
        )
        self._write_section(
            investigation_headers.INVESTIGATION_CONTACTS, section, comments, headers
        )

    def _write_studies(self):
        # Write STUDY sections
        for study in self.investigation.studies:
            self._write_study_basic_info(study)
            self._write_study_design_descriptors(study)
            self._write_study_publications(study)
            self._write_study_factors(study)
            self._write_study_assays(study)
            self._write_study_protocols(study)
            self._write_study_contacts(study)

    def _write_study_basic_info(self, study: models.StudyInfo):
        # Read STUDY INFO section
        basic_info = study.info
        section = {
            investigation_headers.STUDY_IDENTIFIER: [basic_info.identifier],
            investigation_headers.STUDY_TITLE: [basic_info.title],
            investigation_headers.STUDY_DESCRIPTION: [basic_info.description],
            investigation_headers.STUDY_SUBMISSION_DATE: [basic_info.submission_date],
            investigation_headers.STUDY_PUBLIC_RELEASE_DATE: [basic_info.public_release_date],
            investigation_headers.STUDY_FILE_NAME: [basic_info.path],
        }
        comments = _extract_comments([basic_info])
        headers = _extract_section_header(basic_info, investigation_headers.STUDY)
        self._write_section(investigation_headers.STUDY, section, comments, headers)

    def _write_study_design_descriptors(self, study: models.StudyInfo):
        # Read STUDY DESIGN DESCRIPTORS section
        section = _init_multi_column_section(investigation_headers.STUDY_DESIGN_DESCR_KEYS)
        for design in study.designs:
            if (
                hasattr(design.type, "name")
                and hasattr(design.type, "accession")
                and hasattr(design.type, "ontology_name")
            ):
                section[investigation_headers.STUDY_DESIGN_TYPE].append(design.type.name or "")
                section[investigation_headers.STUDY_DESIGN_TYPE_TERM_ACCESSION_NUMBER].append(
                    design.type.accession or ""
                )
                section[investigation_headers.STUDY_DESIGN_TYPE_TERM_SOURCE_REF].append(
                    design.type.ontology_name or ""
                )
            else:
                section[investigation_headers.STUDY_DESIGN_TYPE].append(design.type)
                section[investigation_headers.STUDY_DESIGN_TYPE_TERM_ACCESSION_NUMBER].append("")
                section[investigation_headers.STUDY_DESIGN_TYPE_TERM_SOURCE_REF].append("")
        comments = _extract_comments(study.designs)
        headers = _extract_section_header(
            list(study.designs)[0] if study.designs else None,
            investigation_headers.STUDY_DESIGN_DESCRIPTORS,
        )
        self._write_section(
            investigation_headers.STUDY_DESIGN_DESCRIPTORS, section, comments, headers
        )

    def _write_study_publications(self, study: models.StudyInfo):
        # Write STUDY PUBLICATIONS section
        section = _init_multi_column_section(investigation_headers.STUDY_PUBLICATIONS_KEYS)
        for publication in study.publications:
            section[investigation_headers.STUDY_PUBMED_ID].append(publication.pubmed_id)
            section[investigation_headers.STUDY_PUBLICATION_DOI].append(publication.doi)
            section[investigation_headers.STUDY_PUBLICATION_AUTHOR_LIST].append(publication.authors)
            section[investigation_headers.STUDY_PUBLICATION_TITLE].append(publication.title)
            if (
                hasattr(publication.status, "name")
                and hasattr(publication.status, "accession")
                and hasattr(publication.status, "ontology_name")
            ):
                section[investigation_headers.STUDY_PUBLICATION_STATUS].append(
                    publication.status.name or ""
                )
                section[
                    investigation_headers.STUDY_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER
                ].append(publication.status.accession or "")
                section[investigation_headers.STUDY_PUBLICATION_STATUS_TERM_SOURCE_REF].append(
                    publication.status.ontology_name or ""
                )
            else:
                section[investigation_headers.STUDY_PUBLICATION_STATUS].append(publication.status)
                section[
                    investigation_headers.STUDY_PUBLICATION_STATUS_TERM_ACCESSION_NUMBER
                ].append("")
                section[investigation_headers.STUDY_PUBLICATION_STATUS_TERM_SOURCE_REF].append("")
        comments = _extract_comments(study.publications)
        headers = _extract_section_header(
            list(study.publications)[0] if study.publications else None,
            investigation_headers.STUDY_PUBLICATIONS,
        )
        self._write_section(investigation_headers.STUDY_PUBLICATIONS, section, comments, headers)

    def _write_study_factors(self, study: models.StudyInfo):
        # Write STUDY FACTORS section
        section = _init_multi_column_section(investigation_headers.STUDY_FACTORS_KEYS)
        for factor in study.factors.values():
            section[investigation_headers.STUDY_FACTOR_NAME].append(factor.name)
            if (
                hasattr(factor.type, "name")
                and hasattr(factor.type, "accession")
                and hasattr(factor.type, "ontology_name")
            ):
                section[investigation_headers.STUDY_FACTOR_TYPE].append(factor.type.name)
                section[investigation_headers.STUDY_FACTOR_TYPE_TERM_ACCESSION_NUMBER].append(
                    factor.type.accession
                )
                section[investigation_headers.STUDY_FACTOR_TYPE_TERM_SOURCE_REF].append(
                    factor.type.ontology_name
                )
            else:
                section[investigation_headers.STUDY_FACTOR_TYPE].append(factor.type)
                section[investigation_headers.STUDY_FACTOR_TYPE_TERM_ACCESSION_NUMBER].append("")
                section[investigation_headers.STUDY_FACTOR_TYPE_TERM_SOURCE_REF].append("")
        comments = _extract_comments(study.factors.values())
        headers = _extract_section_header(
            list(study.factors.values())[0] if study.factors else None,
            investigation_headers.STUDY_FACTORS,
        )
        self._write_section(investigation_headers.STUDY_FACTORS, section, comments, headers)

    def _write_study_assays(self, study: models.StudyInfo):
        # Write STUDY ASSAYS section
        section = _init_multi_column_section(investigation_headers.STUDY_ASSAYS_KEYS)
        for assay in study.assays.values():
            section[investigation_headers.STUDY_ASSAY_FILE_NAME].append(assay.path)

            if (
                hasattr(assay.measurement_type, "name")
                and hasattr(assay.measurement_type, "accession")
                and hasattr(assay.measurement_type, "ontology_name")
            ):
                section[investigation_headers.STUDY_ASSAY_MEASUREMENT_TYPE].append(
                    assay.measurement_type.name or ""
                )
                section[
                    investigation_headers.STUDY_ASSAY_MEASUREMENT_TYPE_TERM_ACCESSION_NUMBER
                ].append(assay.measurement_type.accession or "")
                section[investigation_headers.STUDY_ASSAY_MEASUREMENT_TYPE_TERM_SOURCE_REF].append(
                    assay.measurement_type.ontology_name or ""
                )
            else:
                section[investigation_headers.STUDY_ASSAY_MEASUREMENT_TYPE].append(
                    assay.measurement_type
                )
                section[
                    investigation_headers.STUDY_ASSAY_MEASUREMENT_TYPE_TERM_ACCESSION_NUMBER
                ].append("")
                section[investigation_headers.STUDY_ASSAY_MEASUREMENT_TYPE_TERM_SOURCE_REF].append(
                    ""
                )

            if (
                hasattr(assay.technology_type, "name")
                and hasattr(assay.technology_type, "accession")
                and hasattr(assay.technology_type, "ontology_name")
            ):
                section[investigation_headers.STUDY_ASSAY_TECHNOLOGY_TYPE].append(
                    assay.technology_type.name or ""
                )
                section[
                    investigation_headers.STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_ACCESSION_NUMBER
                ].append(assay.technology_type.accession or "")
                section[investigation_headers.STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_SOURCE_REF].append(
                    assay.technology_type.ontology_name or ""
                )
            else:
                section[investigation_headers.STUDY_ASSAY_TECHNOLOGY_TYPE].append(
                    assay.technology_type
                )
                section[
                    investigation_headers.STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_ACCESSION_NUMBER
                ].append("")
                section[investigation_headers.STUDY_ASSAY_TECHNOLOGY_TYPE_TERM_SOURCE_REF].append(
                    ""
                )

            section[investigation_headers.STUDY_ASSAY_TECHNOLOGY_PLATFORM].append(assay.platform)

        comments = _extract_comments(study.assays.values())
        headers = _extract_section_header(
            list(study.assays.values())[0] if study.assays else None,
            investigation_headers.STUDY_ASSAYS,
        )
        self._write_section(investigation_headers.STUDY_ASSAYS, section, comments, headers)

    def _write_study_protocols(self, study: models.StudyInfo):
        # Write STUDY PROTOCOLS section
        section = _init_multi_column_section(investigation_headers.STUDY_PROTOCOLS_KEYS)
        for protocol in study.protocols.values():
            section[investigation_headers.STUDY_PROTOCOL_NAME].append(protocol.name)

            if (
                hasattr(protocol.type, "name")
                and hasattr(protocol.type, "accession")
                and hasattr(protocol.type, "ontology_name")
            ):
                section[investigation_headers.STUDY_PROTOCOL_TYPE].append(protocol.type.name or "")
                section[investigation_headers.STUDY_PROTOCOL_TYPE_TERM_ACCESSION_NUMBER].append(
                    protocol.type.accession or ""
                )
                section[investigation_headers.STUDY_PROTOCOL_TYPE_TERM_SOURCE_REF].append(
                    protocol.type.ontology_name or ""
                )
            else:
                section[investigation_headers.STUDY_PROTOCOL_TYPE].append(protocol.type)
                section[investigation_headers.STUDY_PROTOCOL_TYPE_TERM_ACCESSION_NUMBER].append("")
                section[investigation_headers.STUDY_PROTOCOL_TYPE_TERM_SOURCE_REF].append("")

            section[investigation_headers.STUDY_PROTOCOL_DESCRIPTION].append(protocol.description)
            section[investigation_headers.STUDY_PROTOCOL_URI].append(protocol.uri)
            section[investigation_headers.STUDY_PROTOCOL_VERSION].append(protocol.version)

            names = list()
            accessions = list()
            ontologies = list()
            for parameter in protocol.parameters.values():
                if (
                    hasattr(parameter, "name")
                    and hasattr(parameter, "accession")
                    and hasattr(parameter, "ontology_name")
                ):
                    names.append(parameter.name or "")
                    accessions.append(parameter.accession or "")
                    ontologies.append(parameter.ontology_name or "")
                else:
                    names.append(parameter.name)
                    accessions.append("")
                    ontologies.append("")
            section[investigation_headers.STUDY_PROTOCOL_PARAMETERS_NAME].append(";".join(names))
            section[
                investigation_headers.STUDY_PROTOCOL_PARAMETERS_NAME_TERM_ACCESSION_NUMBER
            ].append(";".join(accessions))
            section[investigation_headers.STUDY_PROTOCOL_PARAMETERS_NAME_TERM_SOURCE_REF].append(
                ";".join(ontologies)
            )

            names = list()
            types = list()
            accessions = list()
            ontologies = list()
            for component in protocol.components.values():
                names.append(component.name)
                if (
                    hasattr(component.type, "name")
                    and hasattr(component.type, "accession")
                    and hasattr(component.type, "ontology_name")
                ):
                    types.append(component.type.name or "")
                    accessions.append(component.type.accession or "")
                    ontologies.append(component.type.ontology_name or "")
                else:
                    names.append(component.type)
                    accessions.append("")
                    ontologies.append("")
            section[investigation_headers.STUDY_PROTOCOL_COMPONENTS_NAME].append(";".join(names))
            section[investigation_headers.STUDY_PROTOCOL_COMPONENTS_TYPE].append(";".join(types))
            section[
                investigation_headers.STUDY_PROTOCOL_COMPONENTS_TYPE_TERM_ACCESSION_NUMBER
            ].append(";".join(accessions))
            section[investigation_headers.STUDY_PROTOCOL_COMPONENTS_TYPE_TERM_SOURCE_REF].append(
                ";".join(ontologies)
            )

        comments = _extract_comments(study.protocols.values())
        headers = _extract_section_header(
            list(study.protocols.values())[0] if study.protocols else None,
            investigation_headers.STUDY_PROTOCOLS,
        )
        self._write_section(investigation_headers.STUDY_PROTOCOLS, section, comments, headers)

    def _write_study_contacts(self, study: models.StudyInfo):
        # Write STUDY CONTACTS section
        section = _init_multi_column_section(investigation_headers.STUDY_CONTACTS_KEYS)
        for contact in study.contacts:
            section[investigation_headers.STUDY_PERSON_LAST_NAME].append(contact.last_name)
            section[investigation_headers.STUDY_PERSON_FIRST_NAME].append(contact.first_name)
            section[investigation_headers.STUDY_PERSON_MID_INITIALS].append(contact.mid_initial)
            section[investigation_headers.STUDY_PERSON_EMAIL].append(contact.email)
            section[investigation_headers.STUDY_PERSON_PHONE].append(contact.phone)
            section[investigation_headers.STUDY_PERSON_FAX].append(contact.fax)
            section[investigation_headers.STUDY_PERSON_ADDRESS].append(contact.address)
            section[investigation_headers.STUDY_PERSON_AFFILIATION].append(contact.affiliation)
            if (
                hasattr(contact.role, "name")
                and hasattr(contact.role, "accession")
                and hasattr(contact.role, "ontology_name")
            ):
                section[investigation_headers.STUDY_PERSON_ROLES].append(contact.role.name or "")
                section[investigation_headers.STUDY_PERSON_ROLES_TERM_ACCESSION_NUMBER].append(
                    contact.role.accession or ""
                )
                section[investigation_headers.STUDY_PERSON_ROLES_TERM_SOURCE_REF].append(
                    contact.role.ontology_name or ""
                )
            else:
                section[investigation_headers.STUDY_PERSON_ROLES].append(contact.role)
                section[investigation_headers.STUDY_PERSON_ROLES_TERM_ACCESSION_NUMBER].append("")
                section[investigation_headers.STUDY_PERSON_ROLES_TERM_SOURCE_REF].append("")
        comments = _extract_comments(study.contacts)
        headers = _extract_section_header(
            list(study.contacts)[0] if study.contacts else None,
            investigation_headers.STUDY_CONTACTS,
        )
        self._write_section(investigation_headers.STUDY_CONTACTS, section, comments, headers)

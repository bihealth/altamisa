# -*- coding: utf-8 -*-
"""Validation of an ISA investigation

Eventually, all format independent content- and specification-related validations which
don't interrupt model creation definitely (e.g. when parsing from ISA-tab) should go
here. Then, validations can be performed on whole models (e.g. after parsing or before
writing) and provide a comprehensive list of warnings of different degree.
"""

import re
from typing import Dict, Tuple
import warnings

from . import models
from ..exceptions import (
    AdvisoryIsaValidationWarning,
    CriticalIsaValidationWarning,
    ModerateIsaValidationWarning,
)
from .validate_assay_study import _OntologyTermRefValidator

__author__ = "Mathias Kuhring <mathias.kuhring@bih-charite.de>"


# Pattern and helper functions for validation ------------------------------------------------------


# DATE_PATTERN = re.compile("^\\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$")
MAIL_PATTERN = re.compile("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$")
PHONE_PATTERN = re.compile("^\\+?[\\d /()-]+$")  # only checks characters!
DOI_PATTERN = re.compile("^(?:(?:DOI|doi):)?10[.][0-9]{4,}(?:[.][0-9]+)*/\\S+$")
PMID_PATTERN = re.compile("^\\d+$")


def _validate_mail_address(mail_address: str) -> None:
    """Helper function to validate mail strings"""
    if mail_address and not MAIL_PATTERN.match(mail_address):
        msg = f"Invalid mail address: {mail_address}"
        warnings.warn(msg, AdvisoryIsaValidationWarning)


def _validate_phone_number(phone_number: str) -> None:
    """Helper function to validate phone/fax number strings"""
    if phone_number and not PHONE_PATTERN.match(phone_number):
        msg = f"Invalid phone/fax number: {phone_number}"
        warnings.warn(msg, AdvisoryIsaValidationWarning)


def _validate_doi(doi: str) -> None:
    """Helper function to validate doi strings"""
    if doi and not DOI_PATTERN.match(doi):
        msg = f"Invalid doi string: {doi}"
        warnings.warn(msg, AdvisoryIsaValidationWarning)


def _validate_pubmed_id(pubmed_id: str) -> None:
    """Helper function to validate pubmed id strings"""
    if pubmed_id and not PMID_PATTERN.match(pubmed_id):
        msg = f"Invalid pubmed_id string: {pubmed_id}"
        warnings.warn(msg, AdvisoryIsaValidationWarning)


# Validator classes --------------------------------------------------------------------


class InvestigationValidator:
    """
    Validator for Investigation

    :type investigation: models.InvestigationInfo
    :param investigation: The investigation model to validate
    """

    def __init__(self, investigation: models.InvestigationInfo):
        self._investigation = investigation
        self._ontology_validator = _OntologyTermRefValidator(investigation.ontology_source_refs)
        self._study_ids = set()
        self._study_paths = set()
        self._study_titles = set()
        self._assay_paths = set()

    def validate(self):
        """Validate the investigation"""
        self._validate_ontology_sources()
        self._validate_sections()

    def _validate_ontology_sources(self):
        for source in self._investigation.ontology_source_refs.values():
            # Check that ontology sources are complete
            if not all((source.name, source.file, source.version, source.description)):
                msg = (
                    f"Incomplete ontology source; found: {source.name}, {source.file}, "
                    f"{source.version}, {source.description}, {source.comments}"
                )
                warnings.warn(msg, CriticalIsaValidationWarning)
            # Check that ontology source names contain no whitespaces
            if re.search("\\s", source.name):
                msg = (
                    f"Ontology source name including whitespace(s); found: {source.name}, "
                    f"{source.file}, {source.version}, {source.description}, {source.comments}"
                )
                warnings.warn(msg, AdvisoryIsaValidationWarning)

    def _validate_sections(self):
        self._validate_investigation_info()
        self._validate_publications(self._investigation.publications)
        self._validate_contacts(self._investigation.contacts)
        self._validate_studies()

    def _validate_investigation_info(self):
        info = self._investigation.info
        # If only one study is available, metadata should be recorded in the study section
        # (https://isa-specs.readthedocs.io/en/latest/isatab.html#investigation-section)
        if len(self._investigation.studies) == 1:
            if any((info.title, info.description, info.submission_date, info.public_release_date)):
                msg = (
                    "Investigation with only one study contains metadata:\n"
                    f"\tID:\t{info.identifier}\n\tTitle:\t{info.title}\n"
                    f"\tPath:\t{info.path or ''}\n\tDescription:\t{info.description}\n"
                    f"\tSubmission Date:\t{info.submission_date}\n"
                    f"\tPublic Release Date:\t{info.public_release_date}\n"
                    "\tPrefer recording metadata in the study section."
                )
                warnings.warn(msg, ModerateIsaValidationWarning)
        # If more than one study is available, investigation should at least contain an id and title
        else:
            # Validate availability of investigation identifier
            if not info.identifier:
                msg = (
                    "Investigation without identifier:\n"
                    f"Title:\t{info.title}\nPath:\t{info.path or ''}"
                )
                warnings.warn(msg, ModerateIsaValidationWarning)
            # Validate availability of investigation title
            if not info.title:
                msg = (
                    "Investigation without title:\n"
                    f"ID:\t{info.identifier}\nPath:\t{info.path or ''}"
                )
                warnings.warn(msg, ModerateIsaValidationWarning)

    def _validate_studies(self):
        # Check if any study exists
        if not self._investigation.studies:
            msg = f"No studies declared in investigation: {self._investigation.info.path}"
            warnings.warn(msg, CriticalIsaValidationWarning)
            return
        for study in self._investigation.studies:
            # Validate availability of minimal study information (ids, paths, titles)
            if not (study.info.identifier and study.info.path):
                msg = (
                    "Study with incomplete minimal information (ID and path):"
                    f"\nID:\t{study.info.identifier}\nTitle:\t{study.info.title}\n"
                    f"Path:\t{study.info.path or ''}"
                )
                warnings.warn(msg, CriticalIsaValidationWarning)
            if not study.info.title:
                msg = (
                    "Study without title:\n"
                    f"ID:\t{study.info.identifier}\nTitle:\t{study.info.title}\n"
                    f"Path:\t{study.info.path or ''}"
                )
                warnings.warn(msg, ModerateIsaValidationWarning)
            # Assure distinct studies, i.e. unique ids, paths and preferably titles
            if study.info.identifier in self._study_ids:
                msg = f"Study identifier used more than once: {study.info.identifier}"
                warnings.warn(msg, CriticalIsaValidationWarning)
            else:
                self._study_ids.add(study.info.identifier)
            if study.info.path:
                if study.info.path in self._study_paths:
                    msg = f"Study path used more than once: {study.info.path or ''}"
                    warnings.warn(msg, CriticalIsaValidationWarning)
                else:
                    self._study_paths.add(study.info.path)
            if study.info.title:
                if study.info.title in self._study_titles:
                    msg = f"Study title used more than once: {study.info.title}"
                    warnings.warn(msg, ModerateIsaValidationWarning)
                else:
                    self._study_titles.add(study.info.title)
            # Validate study sections
            self._validate_publications(study.publications)
            self._validate_contacts(study.contacts)
            self._validate_designs(study.designs)
            self._validate_factors(study.factors)
            self._validate_assays(study.assays, study.info.identifier)
            self._validate_protocols(study.protocols)

    def _validate_publications(self, publications: Tuple[models.PublicationInfo, ...]):
        # Validate format of specific fields in publications
        for publication in publications:
            _validate_pubmed_id(publication.pubmed_id)
            _validate_doi(publication.doi)
            if isinstance(publication.status, models.OntologyTermRef):
                self._ontology_validator.validate(publication.status)

    def _validate_contacts(self, contacts: Tuple[models.ContactInfo, ...]):
        # Validate format of specific fields in contacts
        for contact in contacts:
            _validate_mail_address(contact.email)
            _validate_phone_number(contact.phone)
            _validate_phone_number(contact.fax)
            if isinstance(contact.role, models.OntologyTermRef):
                self._ontology_validator.validate(contact.role)

    def _validate_designs(self, designs: Tuple[models.DesignDescriptorsInfo, ...]):
        # Validate format of specific fields in designs
        for design in designs:
            if isinstance(design.type, models.OntologyTermRef):
                self._ontology_validator.validate(design.type)

    def _validate_factors(self, factors: Dict[str, models.FactorInfo]):
        # Validate format of specific fields in factors
        for factor in factors.values():
            if isinstance(factor.type, models.OntologyTermRef):
                self._ontology_validator.validate(factor.type)

    def _validate_assays(self, assays: Tuple[models.AssayInfo, ...], study_id: str):
        # Check if any assays exists (according to specs, having an assays is not mandatory)
        if not assays:
            msg = (
                f'No assays declared in study "{study_id}" of '
                f'investigation "{self._investigation.info.path}"'
            )
            warnings.warn(msg, AdvisoryIsaValidationWarning)
            return
        for assay in assays:
            # Validate availability of minimal assay information
            # (path, measurement type, technology type and technology platform)
            meas_type = (
                assay.measurement_type.name
                if isinstance(assay.measurement_type, models.OntologyTermRef)
                else assay.measurement_type
            )
            tech_type = (
                assay.technology_type.name
                if isinstance(assay.technology_type, models.OntologyTermRef)
                else assay.technology_type
            )
            if not (assay.path and meas_type and tech_type):
                msg = (
                    "Assay with incomplete minimal information (path, measurement and "
                    f"technology type):\nPath:\t{assay.path or ''}\n"
                    f"Measurement Type:\t{meas_type}\nTechnology Type:\t{tech_type}\n"
                    f"Technology Platform:\t{assay.platform}"
                )
                warnings.warn(msg, CriticalIsaValidationWarning)
            if not assay.platform:
                msg = (
                    f"Assay without platform:\nPath:\t{assay.path or ''}"
                    f"\nMeasurement Type:\t{meas_type}\nTechnology Type:\t{tech_type}\n"
                    f"Technology Platform:\t{assay.platform}"
                )
                warnings.warn(msg, AdvisoryIsaValidationWarning)
            # Assure distinct assays, i.e. unique paths
            if assay.path:
                if assay.path in self._assay_paths:
                    msg = f"Assay path used more than once: {assay.path or ''}"
                    warnings.warn(msg, CriticalIsaValidationWarning)
                else:
                    self._assay_paths.add(assay.path)
            # Validate format of specific fields in assays
            if isinstance(assay.measurement_type, models.OntologyTermRef):
                self._ontology_validator.validate(assay.measurement_type)
            if isinstance(assay.technology_type, models.OntologyTermRef):
                self._ontology_validator.validate(assay.technology_type)

    def _validate_protocols(self, protocols: Dict[str, models.ProtocolInfo]):
        # Validate format of specific fields in protocols
        for protocol in protocols.values():
            if isinstance(protocol.type, models.OntologyTermRef):
                self._ontology_validator.validate(protocol.type)
            for parameter in protocol.parameters.values():
                if isinstance(parameter, models.OntologyTermRef):
                    self._ontology_validator.validate(parameter)
            for component in protocol.components.values():
                if isinstance(component.type, models.OntologyTermRef):
                    self._ontology_validator.validate(component.type)

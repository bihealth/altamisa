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

from ..exceptions import (
    AdvisoryIsaValidationWarning,
    CriticalIsaValidationWarning,
    ModerateIsaValidationWarning,
)
from .helpers import is_ontology_term_ref
from . import models
from .validate_assay_study import _OntologyTermRefValidator


__author__ = "Mathias Kuhring <mathias.kuhring@bihealth.de>"


# Pattern and helper functions for validation ------------------------------------------------------


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
        warnings.warn(msg, AdvisoryIsaValidationWarning)


def _validate_phone_number(phone_number) -> str:
    """Helper function to validate phone/fax number strings"""
    if phone_number and not PHONE_PATTERN.match(phone_number):
        tpl = "Invalid phone/fax number: {}"
        msg = tpl.format(phone_number)
        warnings.warn(msg, AdvisoryIsaValidationWarning)


def _validate_doi(doi) -> str:
    """Helper function to validate doi strings"""
    if doi and not DOI_PATTERN.match(doi):
        tpl = "Invalid doi string: {}"
        msg = tpl.format(doi)
        warnings.warn(msg, AdvisoryIsaValidationWarning)


def _validate_pubmed_id(pubmed_id) -> str:
    """Helper function to validate pubmed id strings"""
    if pubmed_id and not PMID_PATTERN.match(pubmed_id):
        tpl = "Invalid pubmed_id string: {}"
        msg = tpl.format(pubmed_id)
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
                tpl = "Incomplete ontology source; found: {}, {}, {}, {}, {}"
                msg = tpl.format(
                    source.name, source.file, source.version, source.description, source.comments
                )
                warnings.warn(msg, CriticalIsaValidationWarning)
            # Check that ontology source names contain no whitespaces
            if re.search("\\s", source.name):
                tpl = "Ontology source name including whitespace(s); found: {}, {}, {}, {}, {}"
                msg = tpl.format(
                    source.name, source.file, source.version, source.description, source.comments
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
                tpl = (
                    "Investigation with only one study contains metadata:\n\tID:\t{}\n\tTitle:\t"
                    "{}\n\tPath:\t{}\n\tSubmission Date:\t{}\n\tPublic Release Date:\t{"
                    "}\n\tPrefer recording metadata in the study section."
                )
                msg = tpl.format(
                    info.identifier,
                    info.title,
                    info.path or "",
                    info.description,
                    info.submission_date,
                    info.public_release_date,
                )
                warnings.warn(msg, ModerateIsaValidationWarning)
        # If more than one study is available, investigation should at least contain an id and title
        else:
            # Validate availability of investigation identifier
            if not info.identifier:
                tpl = "Investigation without identifier:\nTitle:\t{}\nPath:\t{}"
                msg = tpl.format(info.title, info.path or "")
                warnings.warn(msg, ModerateIsaValidationWarning)
            # Validate availability of investigation title
            if not info.title:
                tpl = "Investigation without title:\nID:\t{}\nPath:\t{}"
                msg = tpl.format(info.identifier, info.path or "")
                warnings.warn(msg, ModerateIsaValidationWarning)

    def _validate_studies(self):
        # Check if any study exists
        if not self._investigation.studies:
            tpl = "No studies declared in investigation: {}"
            msg = tpl.format(self._investigation.info.path)
            warnings.warn(msg, CriticalIsaValidationWarning)
            return
        for study in self._investigation.studies:
            # Validate availability of minimal study information (ids, paths, titles)
            if not (study.info.identifier and study.info.path):
                tpl = (
                    "Study with incomplete minimal information (ID and path):"
                    "\nID:\t{}\nTitle:\t{}\nPath:\t{}"
                )
                msg = tpl.format(study.info.identifier, study.info.title, study.info.path or "")
                warnings.warn(msg, CriticalIsaValidationWarning)
            if not study.info.title:
                tpl = "Study without title:\nID:\t{}\nTitle:\t{}\nPath:\t{}"
                msg = tpl.format(study.info.identifier, study.info.title, study.info.path or "")
                warnings.warn(msg, ModerateIsaValidationWarning)
            # Assure distinct studies, i.e. unique ids, paths and preferably titles
            if study.info.identifier in self._study_ids:
                tpl = "Study identifier used more than once: {}"
                msg = tpl.format(study.info.identifier)
                warnings.warn(msg, CriticalIsaValidationWarning)
            else:
                self._study_ids.add(study.info.identifier)
            if study.info.path:
                if study.info.path in self._study_paths:
                    tpl = "Study path used more than once: {}"
                    msg = tpl.format(study.info.path or "")
                    warnings.warn(msg, CriticalIsaValidationWarning)
                else:
                    self._study_paths.add(study.info.path)
            if study.info.title:
                if study.info.title in self._study_titles:
                    tpl = "Study title used more than once: {}"
                    msg = tpl.format(study.info.title)
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

    def _validate_publications(self, publications: Tuple[models.PublicationInfo]):
        # Validate format of specific fields in publications
        for publication in publications:
            _validate_pubmed_id(publication.pubmed_id)
            _validate_doi(publication.doi)
            if is_ontology_term_ref(publication.status):
                self._ontology_validator.validate(publication.status)

    def _validate_contacts(self, contacts: Tuple[models.ContactInfo]):
        # Validate format of specific fields in contacts
        for contact in contacts:
            _validate_mail_address(contact.email)
            _validate_phone_number(contact.phone)
            _validate_phone_number(contact.fax)
            if is_ontology_term_ref(contact.role):
                self._ontology_validator.validate(contact.role)

    def _validate_designs(self, designs: Tuple[models.DesignDescriptorsInfo]):
        # Validate format of specific fields in designs
        for design in designs:
            if is_ontology_term_ref(design.type):
                self._ontology_validator.validate(design.type)

    def _validate_factors(self, factors: Dict[str, models.FactorInfo]):
        # Validate format of specific fields in factors
        for factor in factors.values():
            if is_ontology_term_ref(factor.type):
                self._ontology_validator.validate(factor.type)

    def _validate_assays(self, assays: Tuple[models.AssayInfo], study_id: str):
        # Check if any assays exists (according to specs, having an assays is not mandatory)
        if not assays:
            tpl = "No assays declared in study '{}' of investigation '{}'"
            msg = tpl.format(study_id, self._investigation.info.path)
            warnings.warn(msg, AdvisoryIsaValidationWarning)
            return
        for assay in assays:
            # Validate availability of minimal assay information
            # (path, measurement type, technology type and technology platform)
            meas_type = (
                assay.measurement_type.name
                if is_ontology_term_ref(assay.measurement_type)
                else assay.measurement_type
            )
            tech_type = (
                assay.technology_type.name
                if is_ontology_term_ref(assay.technology_type)
                else assay.technology_type
            )
            if not (assay.path and meas_type and tech_type):
                tpl = (
                    "Assay with incomplete minimal information (path, measurement and "
                    "technology type):\nPath:\t{}\nMeasurement Type:\t{}\nTechnology Type:\t{"
                    "}\nTechnology Platform:\t{}"
                )
                msg = tpl.format(assay.path or "", meas_type, tech_type, assay.platform)
                warnings.warn(msg, CriticalIsaValidationWarning)
            if not assay.platform:
                tpl = (
                    "Assay without platform:\nPath:\t{}"
                    "\nMeasurement Type:\t{}\nTechnology Type:\t{}\nTechnology Platform:\t{}"
                )
                msg = tpl.format(assay.path or "", meas_type, tech_type, assay.platform)
                warnings.warn(msg, AdvisoryIsaValidationWarning)
            # Assure distinct assays, i.e. unique paths
            if assay.path:
                if assay.path in self._assay_paths:
                    tpl = "Assay path used more than once: {}"
                    msg = tpl.format(assay.path or "")
                    warnings.warn(msg, CriticalIsaValidationWarning)
                else:
                    self._assay_paths.add(assay.path)
            # Validate format of specific fields in assays
            if is_ontology_term_ref(assay.measurement_type):
                self._ontology_validator.validate(assay.measurement_type)
            if is_ontology_term_ref(assay.technology_type):
                self._ontology_validator.validate(assay.technology_type)

    def _validate_protocols(self, protocols: Dict[str, models.ProtocolInfo]):
        # Validate format of specific fields in protocols
        for protocol in protocols.values():
            if is_ontology_term_ref(protocol.type):
                self._ontology_validator.validate(protocol.type)
            for parameter in protocol.parameters.values():
                if is_ontology_term_ref(parameter):
                    self._ontology_validator.validate(parameter)
            for component in protocol.components.values():
                if is_ontology_term_ref(component.type):
                    self._ontology_validator.validate(component.type)

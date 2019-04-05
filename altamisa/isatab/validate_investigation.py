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

from ..exceptions import AdvisoryIsaValidationWarning, CriticalIsaValidationWarning
from .helpers import is_ontology_term_ref
from . import models
from .validate_assay_study import OntologyTermRefValidator


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
    """Validator for Investigation"""

    def __init__(self, investigation: models.InvestigationInfo):
        self._investigation = investigation
        self._ontology_validator = OntologyTermRefValidator(investigation.ontology_source_refs)

    def validate(self):
        self._validate_ontology_sources()
        self._validate_sections()

    def _validate_ontology_sources(self):
        # Check that ontology sources are complete
        for source in self._investigation.ontology_source_refs.values():
            if not all((source.name, source.file, source.version, source.description)):
                tpl = "Incomplete ontology source; found: {}, {}, {}, {}, {}"
                msg = tpl.format(
                    source.name, source.file, source.version, source.description, source.comments
                )
                warnings.warn(msg, CriticalIsaValidationWarning)

    def _validate_sections(self):
        self._validate_publications(self._investigation.publications)
        self._validate_contacts(self._investigation.contacts)
        for study in self._investigation.studies:
            self._validate_publications(study.publications)
            self._validate_contacts(study.contacts)
            self._validate_designs(study.designs)
            self._validate_factors(study.factors)
            self._validate_assays(study.assays)
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

    def _validate_assays(self, assays: Dict[str, models.AssayInfo]):
        # Validate format of specific fields in assays
        for assay in assays.values():
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

# -*- coding: utf-8 -*-
"""Validation of an ISA model or single objects

Eventually, all format independent content- and specification-related validations which
don't interrupt model creation definitely (e.g. when parsing from ISA-tab) should go
here. Then, validations can be performed on whole models (e.g. after parsing or before
writing) and provide a comprehensive list of warnings of different degree.
"""

from typing import Dict, Optional, Union
import warnings

from . import models
from ..constants import table_headers, table_restrictions, table_tokens
from ..exceptions import CriticalIsaValidationWarning, ModerateIsaValidationWarning

__author__ = "Mathias Kuhring <mathias.kuhring@bih-charite.de>"


# Constants to differentiate models when validating materials, processes or arcs
MODEL_TYPE_ASSAY = "assay"
MODEL_TYPE_STUDY = "study"


# Validator classes --------------------------------------------------------------------


class _OntologyTermRefValidator:
    """Validator for OntologyTermRef values"""

    def __init__(self, ontology_source_refs: Dict[str, models.OntologyRef]):
        #: The definition of the ontology source references
        self.ontology_source_refs = ontology_source_refs

    def validate(self, term_ref: models.OntologyTermRef):
        self._validate_completeness(term_ref)
        self._validate_ontology_source(term_ref)

    @staticmethod
    def _validate_completeness(term_ref: models.OntologyTermRef):
        # All three variables must be available, if ontology name or accession is provided
        if term_ref.ontology_name or term_ref.accession:
            if not all((term_ref.name, term_ref.ontology_name, term_ref.accession)):
                msg = (
                    "Incomplete ontology term reference:\n"
                    f"Name: {term_ref.name or '?'}\n"
                    f"Ontology: {term_ref.ontology_name or '?'}\n"
                    f"Accession: {term_ref.accession or '?'}"
                )
                warnings.warn(msg, CriticalIsaValidationWarning)

    def _validate_ontology_source(self, term_ref: models.OntologyTermRef):
        # Ontology_name need to reference an ontology source
        if (
            term_ref.ontology_name
            and self.ontology_source_refs
            and term_ref.ontology_name not in self.ontology_source_refs
        ):
            msg = f'Ontology with name "{term_ref.ontology_name}" not defined in investigation!'
            warnings.warn(msg, CriticalIsaValidationWarning)


class _MaterialValidator:
    """Validator for Material nodes"""

    def __init__(
        self,
        model_type,
        factor_refs: Dict[str, models.FactorInfo],
        ontology_validator: _OntologyTermRefValidator,
        assay_info: Optional[models.AssayInfo] = None,
    ):
        self._model_type = model_type
        self._factor_refs = factor_refs
        self._ontology_validator = ontology_validator
        self._assay_info = assay_info

    def validate(self, material: models.Material):
        """Run Material validations"""
        self._validate_material_annotations(material)
        self._validate_material_naming_start_node(material)
        self._validate_annotation_restrictions(material)
        self._validate_assay_restrictions(material.type)
        self._validate_ontology_term_refs(material)
        self._validate_factor_values(material.factor_values)

    def _validate_material_annotations(self, material: models.Material):
        # Warn about unnamed materials/data files if there are annotations
        def has_content(value):
            if isinstance(value, models.OntologyTermRef):
                return value.name or value.accession or value.ontology_name
            else:
                return value

        any_char = any(
            [any(has_content(v) for v in char.value) for char in material.characteristics]
        )
        any_comm = any([comm.value for comm in material.comments])
        any_fact = any([any(has_content(v) for v in fact.value) for fact in material.factor_values])
        if not material.name and any(
            (
                any_char,
                any_comm,
                any_fact,
                has_content(material.extract_label),
                has_content(material.material_type),
            )
        ):
            msg = f"Found annotated material/file without name: {material}"
            warnings.warn(msg, CriticalIsaValidationWarning)

        # Warn about assay samples containing annotations, as they should be recorded in studies
        if (
            self._model_type == MODEL_TYPE_ASSAY
            and material.type == table_headers.SAMPLE_NAME
            and any((any_char, any_comm, any_fact, material.extract_label, material.material_type))
        ):
            msg = (
                f"Found annotated Sample in assay (should be annotated in studies only): {material}"
            )
            warnings.warn(msg, CriticalIsaValidationWarning)

    def _validate_material_naming_start_node(self, material: models.Material):
        # Warn about unnamed Source or Sample nodes
        if (
            (self._model_type == MODEL_TYPE_STUDY and material.type == table_headers.SOURCE_NAME)
            or (self._model_type == MODEL_TYPE_ASSAY and material.type == table_headers.SAMPLE_NAME)
        ) and not material.name:
            msg = f"Found start node without original name: {material.unique_name}"
            warnings.warn(msg, CriticalIsaValidationWarning)

    @staticmethod
    def _validate_annotation_restrictions(material: models.Material):
        # Restrict certain annotations to corresponding material types
        if material.extract_label and material.type != table_headers.LABELED_EXTRACT_NAME:
            msg = f"Label not applied to Labeled Extract Name: {material.type}."
            warnings.warn(msg, CriticalIsaValidationWarning)

        if material.characteristics and material.type in table_headers.DATA_FILE_HEADERS:
            msg = f"Data nodes don't support Characteristics: {material.characteristics}."
            warnings.warn(msg, CriticalIsaValidationWarning)

        if material.material_type and material.type not in (
            # Only allow for actual materials and not for data files
            table_headers.EXTRACT_NAME,
            table_headers.LABELED_EXTRACT_NAME,
            table_headers.LIBRARY_NAME,
            table_headers.SAMPLE_NAME,
            table_headers.SOURCE_NAME,
        ):
            msg = f"Material Type not applied to proper Material: {material.type}."
            warnings.warn(msg, CriticalIsaValidationWarning)

    def _validate_assay_restrictions(self, type_):
        # Restrict certain materials or file types to corresponding assay measurement and technology
        if self._model_type == MODEL_TYPE_ASSAY and type_ in {
            **table_restrictions.RESTRICTED_MATERIALS_AMEAS,
            **table_restrictions.RESTRICTED_MATERIALS_ATECH,
            **table_restrictions.RESTRICTED_FILES_AMEAS,
            **table_restrictions.RESTRICTED_FILES_ATECH,
        }:
            if self._assay_info is None:
                msg = f"Material/data '{type_}' not recommended for unspecified assay."
                warnings.warn(msg, ModerateIsaValidationWarning)
            else:
                self._validate_single_assay_restriction(
                    type_,
                    "Material",
                    "measurement",
                    self._assay_info.measurement_type,
                    table_restrictions.RESTRICTED_MATERIALS_AMEAS,
                )
                self._validate_single_assay_restriction(
                    type_,
                    "Material",
                    "technology",
                    self._assay_info.technology_type,
                    table_restrictions.RESTRICTED_MATERIALS_ATECH,
                )
                self._validate_single_assay_restriction(
                    type_,
                    "Data",
                    "measurement",
                    self._assay_info.measurement_type,
                    table_restrictions.RESTRICTED_FILES_AMEAS,
                )
                self._validate_single_assay_restriction(
                    type_,
                    "Data",
                    "technology",
                    self._assay_info.technology_type,
                    table_restrictions.RESTRICTED_FILES_ATECH,
                )

    @staticmethod
    def _validate_single_assay_restriction(
        type_, type_group, assay_info_type, assay_info_value, restrictions
    ):
        if type_ in restrictions and assay_info_value.name.lower() not in restrictions[type_]:
            tpl = "{} '{}' not expected for assay {} '{}' (only '{}')"
            msg = tpl.format(
                type_group,
                type_,
                assay_info_type,
                assay_info_value.name,
                "', '".join(restrictions[type_]),
            )
            warnings.warn(msg, ModerateIsaValidationWarning)

    def _validate_ontology_term_refs(self, material: models.Material):
        # Validate consistency of all potential ontology term references in a material
        if isinstance(material.extract_label, models.OntologyTermRef):
            self._ontology_validator.validate(material.extract_label)
        if isinstance(material.material_type, models.OntologyTermRef):
            self._ontology_validator.validate(material.material_type)
        for c in material.characteristics:
            for v in c.value:
                if isinstance(v, models.OntologyTermRef):
                    self._ontology_validator.validate(v)
            if isinstance(c.unit, models.OntologyTermRef):
                self._ontology_validator.validate(c.unit)

    def _validate_factor_values(self, factor_values):
        # Validate whether used factor values are declared in investigation
        for factor in factor_values:
            if factor.name not in self._factor_refs:
                msg = f'Factor "{factor.name}" not declared in investigation'
                warnings.warn(msg, ModerateIsaValidationWarning)


class _ProcessValidator:
    """Validator for Process nodes"""

    def __init__(
        self,
        protocols: Dict[str, models.ProtocolInfo],
        ontology_validator: Optional[_OntologyTermRefValidator] = None,
        assay_info: Optional[models.AssayInfo] = None,
    ):
        self._protocols = protocols
        self._ontology_validator = ontology_validator
        self._assay_info = assay_info

    def validate(self, process: models.Process):
        """Run Process validations"""
        valid_ref = self._validate_protocol_ref(process)
        if valid_ref:
            self._validate_parameter_values(process)
            self._validate_name_types(process)
            self._validate_special_case_annotations(process)
        else:
            msg = (
                "Can't validate parameter values and names for process with "
                f'undeclared protocol "{process.protocol_ref}" and name type "{process.name_type}"'
            )
            warnings.warn(msg, ModerateIsaValidationWarning)
        self._validate_ontology_term_refs(process)

    def _validate_protocol_ref(self, process: models.Process):
        # Check if protocol is declared in corresponding study
        if process.protocol_ref == table_tokens.TOKEN_UNKNOWN:
            return False
        elif process.protocol_ref not in self._protocols:
            msg = f'Protocol "{process.protocol_ref}" not declared in investigation file'
            warnings.warn(msg, CriticalIsaValidationWarning)
            return False
        else:
            return True

    def _validate_parameter_values(self, process: models.Process):
        # Check if parameter value is declared in corresponding protocol
        if process.protocol_ref != table_tokens.TOKEN_UNKNOWN:
            for pv in process.parameter_values:
                if pv.name not in self._protocols[process.protocol_ref].parameters:
                    msg = (
                        f'Parameter Value "{pv.name}" not declared for Protocol '
                        f'"{process.protocol_ref}" in investigation file'
                    )
                    warnings.warn(msg, ModerateIsaValidationWarning)

    def _validate_restrictions(
        self, test, process: models.Process, assay_tech_restrictions, protocol_type_restrictions
    ):
        if test in assay_tech_restrictions or test in protocol_type_restrictions:
            if self._assay_info is None:
                msg = f'"{test}" not supported for unspecified assay.'
                warnings.warn(msg, ModerateIsaValidationWarning)
            else:
                # Check if restricted to assay technology
                self._validate_restrictions_by_assay_tech(test, assay_tech_restrictions)
                # Check if restricted to protocol type
                self._validate_restrictions_by_protocol_type(
                    test, process, protocol_type_restrictions
                )

    def _validate_restrictions_by_assay_tech(self, test, assay_tech_restrictions):
        # Check if restricted to assay technology
        if (
            test in assay_tech_restrictions
            and self._assay_info
            and isinstance(self._assay_info.technology_type, models.OntologyTermRef)
            and self._assay_info.technology_type.name
            and self._assay_info.technology_type.name.lower() not in assay_tech_restrictions[test]
        ):
            tpl = '"{}" not supported by assay technology "{}" (only "{}")'
            msg = tpl.format(
                test,
                self._assay_info.technology_type.name,
                ", ".join(assay_tech_restrictions[test]),
            )
            warnings.warn(msg, ModerateIsaValidationWarning)

    def _validate_restrictions_by_protocol_type(
        self, test, process: models.Process, protocol_type_restrictions
    ):
        # Check if restricted to protocol type
        if test in protocol_type_restrictions:
            # Check prototype with partial matching, as types are sometimes extended
            any_match = False
            protocol = self._protocols[process.protocol_ref]
            if isinstance(protocol.type, models.OntologyTermRef) and protocol.type.name:
                protocol_name = protocol.type.name
            else:
                protocol_name = None
            for res_type in protocol_type_restrictions[test]:
                if isinstance(protocol.type, models.OntologyTermRef) and protocol.type.name:
                    any_match = any_match or res_type in protocol.type.name.lower()
            if not any_match:
                tpl = '"{}" not supported by protocol type "{}" (only "{}")'
                msg = tpl.format(
                    test,
                    protocol_name,
                    ", ".join(protocol_type_restrictions[test]),
                )
                warnings.warn(msg, ModerateIsaValidationWarning)

    def _validate_name_types(self, process: models.Process):
        # Match restricted name types to corresponding assay technologies and protocols
        self._validate_restrictions(
            process.name_type,
            process,
            table_restrictions.RESTRICTED_PROTO_NAMES_ATECH,
            table_restrictions.RESTRICTED_PROTO_NAMES_PTYPE,
        )

    def _validate_special_case_annotations(self, process: models.Process):
        # Match restricted annotations to corresponding assay technologies and protocols
        if process.array_design_ref:
            self._validate_restrictions(
                table_headers.ARRAY_DESIGN_REF,
                process,
                table_restrictions.RESTRICTED_PROTO_ANNOS_ATECH,
                table_restrictions.RESTRICTED_PROTO_ANNOS_PTYPE,
            )
        if process.first_dimension or process.second_dimension:
            self._validate_restrictions(
                table_headers.FIRST_DIMENSION,
                process,
                table_restrictions.RESTRICTED_PROTO_ANNOS_ATECH,
                table_restrictions.RESTRICTED_PROTO_ANNOS_PTYPE,
            )
            self._validate_restrictions(
                table_headers.SECOND_DIMENSION,
                process,
                table_restrictions.RESTRICTED_PROTO_ANNOS_ATECH,
                table_restrictions.RESTRICTED_PROTO_ANNOS_PTYPE,
            )

    def _validate_ontology_term_refs(self, process: models.Process):
        if not self._ontology_validator:
            return  # skip
        # Validate consistency of all potential ontology term references in a process
        for parameter in process.parameter_values:
            for v in parameter.value or []:
                if isinstance(v, models.OntologyTermRef):
                    self._ontology_validator.validate(v)
            if isinstance(parameter.unit, models.OntologyTermRef):
                self._ontology_validator.validate(parameter.unit)
        if isinstance(process.first_dimension, models.OntologyTermRef):
            self._ontology_validator.validate(process.first_dimension)
        if isinstance(process.second_dimension, models.OntologyTermRef):
            self._ontology_validator.validate(process.second_dimension)


class _ArcValidator:
    """Validator for Arcs"""

    def __init__(self, materials, processes, model_type: str):
        self._nodes = {**materials, **processes}
        self._model_type = model_type

    def validate(self, arc: models.Arc):
        """Run Arc validations"""

        # Assay checks
        if self._model_type == MODEL_TYPE_ASSAY:
            # Check that samples only start arcs, i.e. head can't be sample
            head = self._nodes[arc.head]
            if hasattr(head, "type") and head.type == table_headers.SAMPLE_NAME:
                msg = (
                    "Found a sample not starting the assay graph: "
                    f'"{head.name}" ("{head.unique_name}")'
                )
                warnings.warn(msg, CriticalIsaValidationWarning)

        # Study checks
        if self._model_type == MODEL_TYPE_STUDY:
            # Check that sources only start arcs, i.e. head can't be source
            head = self._nodes[arc.head]
            if hasattr(head, "type") and head.type == table_headers.SOURCE_NAME:
                msg = (
                    "Found a source not starting the study graph: "
                    f'"{head.name}" ("{head.unique_name}")'
                )
                warnings.warn(msg, CriticalIsaValidationWarning)
            # Check that samples only start arcs, i.e. tail can't be sample
            tail = self._nodes[arc.tail]
            if hasattr(tail, "type") and tail.type == table_headers.SAMPLE_NAME:
                msg = (
                    "Found a sample not ending the study graph: "
                    f'"{tail.name}" ("{tail.unique_name}")'
                )
                warnings.warn(msg, CriticalIsaValidationWarning)


class _AssayAndStudyValidator:
    """Base validator for Study and Assay"""

    _study_info: models.StudyInfo
    _assay_info: Optional[models.AssayInfo]
    _model: Union[models.Study, models.Assay]
    _model_type: str

    def __init__(self, investigation: models.InvestigationInfo):
        self._ontology_validator = _OntologyTermRefValidator(investigation.ontology_source_refs)

    def validate(self):
        """Validate the study or assay"""
        self._validate_materials()
        self._validate_processes()
        self._validate_arcs()

    def _validate_materials(self):
        # Iterate materials and validate
        validator = _MaterialValidator(
            self._model_type, self._study_info.factors, self._ontology_validator, self._assay_info
        )
        for m in self._model.materials.values():
            validator.validate(m)

    def _validate_processes(self):
        # Iterate processes and validate
        validator = _ProcessValidator(
            self._study_info.protocols, self._ontology_validator, self._assay_info
        )
        for p in self._model.processes.values():
            validator.validate(p)

    def _validate_arcs(self):
        # Iterate arcs and validate
        validator = _ArcValidator(self._model.materials, self._model.processes, self._model_type)
        for a in self._model.arcs:
            validator.validate(a)


class StudyValidator(_AssayAndStudyValidator):
    """
    Validator for Study

    :type investigation: models.InvestigationInfo
    :param investigation: The corresponding investigation model
    :type study_info: models.StudyInfo
    :param study_info: The corresponding study information
    :type study: models.Study
    :param study: The Study model to validate
    """

    _model_type = MODEL_TYPE_STUDY

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        study_info: models.StudyInfo,
        study: models.Study,
    ):
        self._study_info = study_info
        self._assay_info = None
        self._model = study
        super().__init__(investigation)


class AssayValidator(_AssayAndStudyValidator):
    """
    Validator for Assay

    :type investigation: models.InvestigationInfo
    :param investigation: The corresponding investigation model
    :type study_info: models.StudyInfo
    :param study_info: The corresponding study information
    :type assay_info: models.AssayInfo
    :param assay_info: The corresponding assay information
    :type assay: models.Assay
    :param assay: The Assay model to validate
    :type parent_study: models.Study
    :param parent_study: Optional: The parent Study of the current Assay (for extended validation)
    """

    _model_type = MODEL_TYPE_ASSAY

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        study_info: models.StudyInfo,
        assay_info: models.AssayInfo,
        assay: models.Assay,
        parent_study: Optional[models.Study] = None,
    ):
        self._study_info = study_info
        self._assay_info = assay_info
        self._model = assay
        self._parent_study = parent_study
        super().__init__(investigation)

    def validate(self):
        """Validate the assay"""
        # Independent validations
        super().validate()
        # Study-dependent validations
        if self._parent_study:
            self._validate_dependency()

    def _validate_dependency(self):
        """Validate if assay complies with parent study"""
        if not self._parent_study:
            return  # skip

        # Check if all samples in the assays are declared in the parent study
        # Collect materials of type "Sample Name"
        study_samples = [
            m.name
            for m in self._parent_study.materials.values()
            if m.type == table_headers.SAMPLE_NAME
        ]
        assay_samples = [
            m.name for m in self._model.materials.values() if m.type == table_headers.SAMPLE_NAME
        ]
        # Collect and list assay samples missing in study
        samples_not_in_study = [s for s in assay_samples if s not in study_samples]
        if samples_not_in_study:
            tpl = "Found samples in assay '{}' but not in parent study '{}':\\n{}"
            if self._assay_info:
                msg = tpl.format(
                    self._assay_info.path.name if self._assay_info.path else "<unknown>",
                    self._study_info.info.path.name if self._study_info.info.path else "<unknown>",
                    ", ".join(samples_not_in_study),
                )
            else:
                msg = "Found samples in assay but not in parent study"
            warnings.warn(msg, CriticalIsaValidationWarning)

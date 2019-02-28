# -*- coding: utf-8 -*-
"""This module contains code for the parsing of assay and study files.
"""


from __future__ import generator_stop

import csv
from datetime import datetime
from pathlib import Path
from typing import List, TextIO

from ..constants import table_tokens
from ..constants import table_headers
from ..exceptions import ParseIsatabException
from .headers import ColumnHeader, StudyHeaderParser, AssayHeaderParser
from . import models


__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"


class _NodeBuilderBase:
    """Base class for Material and Process builder objects"""

    #: Headers to use for naming
    name_headers = None
    #: Allowed ``column_type``s.
    allowed_column_types = None

    def __init__(
        self,
        ontology_source_refs,
        protocol_refs,
        column_headers: List[ColumnHeader],
        study_id: str,
        assay_id: str,
        assay_info: models.AssayInfo = None,
    ):
        #: The definition of the ontology source references
        self.ontology_source_refs = ontology_source_refs
        #: The definition of the protocol references
        self.protocol_refs = protocol_refs
        #: The column descriptions to build ``Material`` from.
        self.column_headers = column_headers
        #: The "Protocol REF" header, if any
        self.protocol_ref_header = None
        #: The header to use for building names, if any
        self.name_header = None
        #: The headers for the characteristics
        self.characteristic_headers = []
        #: The headers for comments
        self.comment_headers = []
        #: The factor value headers
        self.factor_value_headers = []
        #: The parameter value headers
        self.parameter_value_headers = []
        #: The header for array design ref
        self.array_design_ref = None
        #: The header for array design ref
        self.array_design_ref_header = None
        #: The header for first and second dimension
        self.first_dimension_header = None
        self.second_dimension_header = None
        #: The header for extract label type
        self.extract_label_header = None
        #: The header for material type
        self.material_type_header = None
        #: The header for the performer
        self.performer_header = None
        #: The header for the date
        self.date_header = None
        #: The header for the unit
        self.unit_header = None
        #: Current counter value
        self.counter_value = 0
        #: Assign column headers to their roles (properties above)
        self._assign_column_headers()
        #: Study and assay ids used for unique node naming
        self.study_id = study_id
        self.assay_id = assay_id
        #: The assay information
        self.assay_info = assay_info

    def _next_counter(self):
        """Increment counter value and return"""
        self.counter_value += 1
        return self.counter_value

    def _assign_column_headers(self):  # noqa: C901
        # Record the last column header that is a primary annotation (e.g.,
        # "Characteristics[*]" is but "Term Source REF" is not.
        prev = None
        # Interpret the full sequence of column headers.
        for header in self.column_headers:
            if (
                header.column_type not in self.name_headers
                and header.column_type not in self.allowed_column_types
            ):
                tpl = 'Invalid column type occured "{}" not in {}'
                msg = tpl.format(header.column_type, self.allowed_column_types)
                raise ParseIsatabException(msg)
            # Most headers are not secondary, so make this the default state.
            is_secondary = False
            if header.column_type == table_headers.PROTOCOL_REF:
                assert not self.protocol_ref_header
                self.protocol_ref_header = header
            elif header.column_type in self.name_headers:
                assert not self.name_header
                self.name_header = header
            elif header.column_type == table_headers.CHARACTERISTICS:
                self.characteristic_headers.append(header)
            elif header.column_type == table_headers.COMMENT:
                self.comment_headers.append(header)
            elif header.column_type == table_headers.FACTOR_VALUE:
                self.factor_value_headers.append(header)
            elif header.column_type == table_headers.PARAMETER_VALUE:
                self.parameter_value_headers.append(header)
            elif header.column_type == table_headers.MATERIAL_TYPE:
                if self.material_type_header:
                    tpl = 'Seen "Material Type" header for same entity in ' "col {}"
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.material_type_header = header
            elif header.column_type == table_headers.ARRAY_DESIGN_REF:
                if self.array_design_ref_header:
                    tpl = 'Seen "Array Design REF" header for same entity ' "in col {}"
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.array_design_ref_header = header
            elif header.column_type == table_headers.FIRST_DIMENSION:
                if self.first_dimension_header:
                    tpl = 'Seen "First Dimension" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.first_dimension_header = header
            elif header.column_type == table_headers.SECOND_DIMENSION:
                if self.second_dimension_header:
                    tpl = 'Seen "Second Dimension" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.second_dimension_header = header
            elif header.column_type == table_headers.LABEL:
                if self.extract_label_header:
                    tpl = 'Seen "Label" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.extract_label_header = header
            elif header.column_type == table_headers.DATE:
                if self.date_header:
                    tpl = 'Seen "Date" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.date_header = header
            elif header.column_type == table_headers.PERFORMER:
                if self.performer_header:
                    tpl = 'Seen "Performer" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.performer_header = header
            elif header.column_type == table_headers.TERM_SOURCE_REF:
                # Guard against misuse / errors
                if not prev:
                    tpl = "No primary annotation to annotate with term in " "col {}"
                elif prev.column_type not in (
                    # According to ISA-tab specs, Characteristics, Factor Values,
                    # Parameter Values and Units as well as the special cases First
                    # Dimension and Second Dimension may be annotated with
                    # ontologies. However, official examples and configurations also
                    # feature Label and Material Type with ontologies.
                    table_headers.CHARACTERISTICS,
                    # COMMENT, this one is unclear
                    table_headers.FACTOR_VALUE,
                    table_headers.FIRST_DIMENSION,
                    table_headers.MATERIAL_TYPE,
                    table_headers.LABEL,
                    table_headers.PARAMETER_VALUE,
                    table_headers.SECOND_DIMENSION,
                    table_headers.UNIT,
                ):
                    tpl = (
                        "Ontologies not supported for primary annotation "
                        "'{}' (in col {}).".format(prev.column_type, "{}")
                    )
                elif prev.term_source_ref_header:
                    tpl = 'Seen "Term Source REF" header for same entity ' "in col {}"
                else:
                    tpl = None
                if tpl:
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    # The previous non-secondary header is annotated with an ontology term.
                    prev.term_source_ref_header = header
                    is_secondary = True
            elif header.column_type == table_headers.UNIT:
                if prev.unit_header or prev.column_type == table_headers.UNIT:
                    tpl = 'Seen "Unit" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    # The previous non-secondary header is annotated with a unit.
                    prev.unit_header = header
            # Update is secondary flag or not
            if not is_secondary:
                prev = header

    def _build_complex(self, header, line, klass):
        """Build a complex annotation (e.g., may have term referenc or unit."""
        # First, build the individual components
        value = self._build_freetext_or_term_ref(header, line)
        unit = self._build_freetext_or_term_ref(header.unit_header, line)
        # Then, constructing ``klass`` is easy
        return klass(header.label, value, unit)

    def _build_freetext_or_term_ref(self, header, line: List[str]) -> models.FreeTextOrTermRef:
        if not header:
            return None
        elif header.term_source_ref_header:
            header2 = header.term_source_ref_header
            name = line[header.col_no]
            ontology_name = line[header2.col_no]
            accession = line[header2.col_no + 1]
            return models.OntologyTermRef(name, accession, ontology_name, self.ontology_source_refs)
        else:
            return line[header.col_no]

    def _build_simple_headers_list(self) -> List[str]:
        return [h for headers in self.column_headers for h in headers.get_simple_string()]


class _MaterialBuilder(_NodeBuilderBase):
    """Helper class to construct a ``Material`` object from a line"""

    type_ = table_headers.MATERIAL

    name_headers = table_headers.MATERIAL_NAME_HEADERS

    allowed_column_types = (
        # Primary annotations (not parametrized)
        table_headers.MATERIAL_TYPE,
        # Primary annotations (parametrized)
        table_headers.CHARACTERISTICS,
        table_headers.COMMENT,
        table_headers.FACTOR_VALUE,
        # Secondary annotations
        table_headers.LABEL,
        table_headers.TERM_SOURCE_REF,
        table_headers.UNIT,
    )

    def build(self, line: List[str]) -> models.Material:
        """Build and return ``Material`` from TSV file line."""
        counter_value = self._next_counter()
        # First, build the individual components
        assert self.name_header or self.protocol_ref_header
        type_ = self.name_header.column_type
        assay_id = "-{}".format(self.assay_id) if self.assay_id else ""
        name = line[self.name_header.col_no]
        if name:
            # make material/data names unique by column
            if self.name_header.column_type == table_headers.SOURCE_NAME:
                unique_name = "{}-{}-{}".format(self.study_id, "source", name)
            elif self.name_header.column_type == table_headers.SAMPLE_NAME:
                # use static column identifier "sample-", since the same
                # samples occur in different columns in study and assay
                unique_name = "{}-{}-{}".format(self.study_id, "sample", name)
            else:
                # anything else gets the column id
                unique_name = "{}{}-{}-COL{}".format(
                    self.study_id, assay_id, name, self.name_header.col_no + 1
                )
        else:
            name_val = "{}{}-{} {}-{}-{}".format(
                self.study_id,
                assay_id,
                table_tokens.TOKEN_EMPTY,
                self.name_header.column_type,
                self.name_header.col_no + 1,
                counter_value,
            )
            unique_name = models.AnnotatedStr(name_val, was_empty=True)
        extract_label = self._build_freetext_or_term_ref(self.extract_label_header, line)
        characteristics = tuple(
            self._build_complex(hdr, line, models.Characteristics)
            for hdr in self.characteristic_headers
        )
        comments = tuple(
            models.Comment(hdr.label, line[hdr.col_no]) for hdr in self.comment_headers
        )
        factor_values = tuple(
            self._build_complex(hdr, line, models.FactorValue) for hdr in self.factor_value_headers
        )
        material_type = self._build_freetext_or_term_ref(self.material_type_header, line)
        # Don't accept unnamed materials/data files if there are annotations
        any_char = any([(char.value or char.unit) for char in characteristics])
        any_comm = any([comm.value for comm in comments])
        any_fact = any([(fact.value or fact.unit) for fact in factor_values])
        if not name and any((any_char, any_comm, any_fact, extract_label, material_type)):
            tpl = "Found annotated material/file without name: " "{}, {}, {}, {}, {}, {}, {}"
            msg = tpl.format(
                type_,
                unique_name,
                extract_label,
                characteristics,
                comments,
                factor_values,
                material_type,
            )
            raise ParseIsatabException(msg)
        # Then, constructing ``Material`` is easy
        return models.Material(
            type_,
            unique_name,
            name,
            extract_label,
            characteristics,
            comments,
            factor_values,
            material_type,
            self.assay_info,
            self._build_simple_headers_list(),
        )


class _ProcessBuilder(_NodeBuilderBase):
    """Helper class to construct ``Process`` objects."""

    name_headers = table_headers.PROCESS_NAME_HEADERS

    allowed_column_types = (
        table_headers.PROTOCOL_REF,
        # Primary annotations (not parametrized)
        table_headers.PERFORMER,
        table_headers.DATE,
        # Special annotations (not parametrized)
        table_headers.ARRAY_DESIGN_REF,
        table_headers.FIRST_DIMENSION,
        table_headers.SECOND_DIMENSION,
        # Primary annotations (parametrized)
        table_headers.PARAMETER_VALUE,
        table_headers.COMMENT,
        # Secondary annotations
        table_headers.TERM_SOURCE_REF,
        table_headers.UNIT,
    )

    def build(self, line: List[str]) -> models.Process:
        """Build and return ``Process`` from CSV file."""
        # First, build the individual attributes of ``Process``
        protocol_ref, unique_name, name, name_type = self._build_protocol_ref_and_name(line)
        # Check if protocol is declared in corresponding study
        if protocol_ref != table_tokens.TOKEN_UNKNOWN and protocol_ref not in self.protocol_refs:
            tpl = 'Protocol "{}" not declared in investigation file'
            msg = tpl.format(protocol_ref)
            raise ParseIsatabException(msg)
        if self.date_header and line[self.date_header.col_no]:
            try:
                date = datetime.strptime(line[self.date_header.col_no], "%Y-%m-%d").date()
            except ValueError as e:
                tpl = 'Invalid ISO8601 date "{}"'
                msg = tpl.format(line[self.date_header.col_no])
                raise ParseIsatabException(msg) from e
        else:
            date = None
        if self.performer_header:
            performer = line[self.performer_header.col_no]
        else:
            performer = None
        comments = tuple(
            models.Comment(hdr.label, line[hdr.col_no]) for hdr in self.comment_headers
        )
        parameter_values = tuple(
            self._build_complex(hdr, line, models.ParameterValue)
            for hdr in self.parameter_value_headers
        )
        # Check if parameter value is declared in corresponding protocol
        for pv in parameter_values:
            if pv.name not in self.protocol_refs[protocol_ref].parameters:
                tpl = 'Parameter Value "{}" not declared for Protocol "{}" ' "in investigation file"
                msg = tpl.format(pv.name, protocol_ref)
                raise ParseIsatabException(msg)
        # Check for special case annotations
        array_design_ref = (
            line[self.array_design_ref_header.col_no] if self.array_design_ref_header else None
        )
        first_dimension = self._build_freetext_or_term_ref(self.first_dimension_header, line)
        second_dimension = self._build_freetext_or_term_ref(self.second_dimension_header, line)
        # Then, constructing ``Process`` is easy
        return models.Process(
            protocol_ref,
            unique_name,
            name,
            name_type,
            date,
            performer,
            parameter_values,
            comments,
            array_design_ref,
            first_dimension,
            second_dimension,
            self._build_simple_headers_list(),
        )

    def _build_protocol_ref_and_name(self, line: List[str]):
        # At least one of these headers has to be specified
        assert self.name_header or self.protocol_ref_header
        # Perform case distinction on which case is actually true
        counter_value = self._next_counter()
        assay_id = "-{}".format(self.assay_id) if self.assay_id else ""
        name = None
        name_type = None
        if not self.name_header:
            # Name header is not given, will use auto-generated unique name
            # based on protocol ref.
            protocol_ref = line[self.protocol_ref_header.col_no]
            name_val = "{}{}-{}-{}-{}".format(
                self.study_id,
                assay_id,
                protocol_ref,
                self.protocol_ref_header.col_no + 1,
                counter_value,
            )
            unique_name = models.AnnotatedStr(name_val, was_empty=True)
        elif not self.protocol_ref_header:
            # Name header is given, but protocol ref header is not
            protocol_ref = table_tokens.TOKEN_UNKNOWN
            name = line[self.name_header.col_no]
            name_type = self.name_header.column_type
            if name:  # Use name if available
                unique_name = "{}{}-{}-{}".format(
                    self.study_id, assay_id, name, self.name_header.col_no + 1
                )
            else:  # Empty!
                name_val = "{}{}-{} {}-{}-{}".format(
                    self.study_id,
                    assay_id,
                    table_tokens.TOKEN_ANONYMOUS,
                    self.name_header.column_type.replace(" Name", ""),
                    self.name_header.col_no + 1,
                    counter_value,
                )
                unique_name = models.AnnotatedStr(name_val, was_empty=True)
        else:  # Both header are given
            protocol_ref = line[self.protocol_ref_header.col_no]
            name = line[self.name_header.col_no]
            name_type = self.name_header.column_type
            if name:
                unique_name = "{}{}-{}-{}".format(
                    self.study_id, assay_id, name, self.name_header.col_no + 1
                )
            else:
                name_val = "{}{}-{}-{}-{}".format(
                    self.study_id,
                    assay_id,
                    protocol_ref,
                    self.protocol_ref_header.col_no + 1,
                    counter_value,
                )
                unique_name = models.AnnotatedStr(name_val, was_empty=True)
        if not protocol_ref:
            tpl = "Missing protocol reference in column {}"
            msg = tpl.format(self.protocol_ref_header.col_no + 1)
            raise ParseIsatabException(msg)
        return protocol_ref, unique_name, name, name_type


class _RowBuilderBase:
    """Base class for row builders from study and assay files"""

    #: Registry of column header to node builder
    node_builders = None

    def __init__(
        self,
        ontology_source_refs,
        protocol_refs,
        header: List[ColumnHeader],
        study_id: str,
        assay_id: str = None,
        assay_info: models.AssayInfo = None,
    ):
        self.ontology_source_refs = ontology_source_refs
        self.protocol_refs = protocol_refs
        self.header = header
        self.study_id = study_id
        self.assay_id = assay_id
        self.assay_info = assay_info
        self._builders = list(self._make_builders())

    def _make_builders(self):
        """Construct the builder objects for the objects"""
        breaks = list(self._make_breaks())
        for start, end in zip(breaks, breaks[1:]):
            klass = self.node_builders[self.header[start].column_type]
            yield klass(
                self.ontology_source_refs,
                self.protocol_refs,
                self.header[start:end],
                self.study_id,
                self.assay_id,
                self.assay_info,
            )

    def _make_breaks(self):
        """Build indices to break the columns at

        Life would be simpler if ISA-Tab would require a "Protocol REF"
        before generic or specialized assay names (e.g., "Assay Name" or
        "MS Assay Name") or at least define what happens if we see
        ("Protocol REF", "Assay Name", "Assay Name").

        Our interpretation is that in the case above the first "Assay Name"
        further qualifies (=annotates) the "Protocol REF") and the second
        leads to an implicit "Protocol REF" creation with all cell values
        set to "unknown".  This somewhat emulates what the official ISA-Tab
        API does.
        """
        # Record whether we have seen a "Protocol REF" but no "Assay Name".
        noname_protocol_ref = False
        for i, col_hdr in enumerate(self.header):
            if col_hdr.column_type in table_headers.MATERIAL_NAME_HEADERS:
                noname_protocol_ref = False
                yield i
            elif col_hdr.column_type in self.node_builders:
                # Column type has an associated node builder, can be
                # "Protocol REF", an annotating assay name, or implicitely
                # start a new process node.
                if col_hdr.column_type == "Protocol REF":
                    noname_protocol_ref = True
                    yield i
                else:
                    if not noname_protocol_ref:
                        # This one does not annotate a previous "Protocol
                        # REF" because we have already seen a name (it
                        # does not matter whether standalone or giving a
                        # name to a "Protocol REF").
                        yield i
                    # In any case, we have seen a name for a protocol now
                    noname_protocol_ref = False
        yield len(self.header)  # index to end of list

    def build(self, line):
        return [b.build(line) for b in self._builders]


class _StudyRowBuilder(_RowBuilderBase):
    """Build a row from an ISA-TAB study file."""

    node_builders = {
        # Material node builders
        table_headers.SOURCE_NAME: _MaterialBuilder,
        table_headers.SAMPLE_NAME: _MaterialBuilder,
        # Process node builders
        table_headers.PROTOCOL_REF: _ProcessBuilder,
    }


class _AssayRowBuilder(_RowBuilderBase):
    """Build a row from an ISA-TAB assay file."""

    node_builders = {
        # Material node builders
        table_headers.SAMPLE_NAME: _MaterialBuilder,
        table_headers.EXTRACT_NAME: _MaterialBuilder,
        table_headers.LABELED_EXTRACT_NAME: _MaterialBuilder,
        # Data node builders
        table_headers.ARRAY_DATA_FILE: _MaterialBuilder,
        table_headers.ARRAY_DATA_MATRIX_FILE: _MaterialBuilder,
        table_headers.ARRAY_DESIGN_FILE: _MaterialBuilder,
        table_headers.DERIVED_ARRAY_DATA_FILE: _MaterialBuilder,
        table_headers.DERIVED_ARRAY_DATA_MATRIX_FILE: _MaterialBuilder,
        table_headers.DERIVED_DATA_FILE: _MaterialBuilder,
        table_headers.DERIVED_SPECTRAL_DATA_FILE: _MaterialBuilder,
        table_headers.IMAGE_FILE: _MaterialBuilder,
        table_headers.METABOLITE_ASSIGNMENT_FILE: _MaterialBuilder,
        table_headers.PEPTIDE_ASSIGNMENT_FILE: _MaterialBuilder,
        table_headers.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE: _MaterialBuilder,
        table_headers.PROTEIN_ASSIGNMENT_FILE: _MaterialBuilder,
        table_headers.RAW_DATA_FILE: _MaterialBuilder,
        table_headers.RAW_SPECTRAL_DATA_FILE: _MaterialBuilder,
        table_headers.SPOT_PICKING_FILE: _MaterialBuilder,
        # Process node builders
        table_headers.ASSAY_NAME: _ProcessBuilder,
        table_headers.DATA_TRANSFORMATION_NAME: _ProcessBuilder,
        table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME: _ProcessBuilder,
        table_headers.HYBRIDIZATION_ASSAY_NAME: _ProcessBuilder,
        table_headers.MS_ASSAY_NAME: _ProcessBuilder,
        table_headers.NORMALIZATION_NAME: _ProcessBuilder,
        table_headers.PROTOCOL_REF: _ProcessBuilder,
        table_headers.SCAN_NAME: _ProcessBuilder,
    }


class _AssayAndStudyBuilder:
    """Helper for building ``Assay`` and ``Study`` objects."""

    def __init__(self, file_name, header, klass):
        self.file_name = file_name
        self.header = header
        self.klass = klass

    def build(self, rows):
        return self._construct(self._postprocess_rows(rows))

    def _postprocess_rows(self, rows):
        """Postprocess the ``rows``.

        Right now we are looking for nodes (material of process) without an
        original name (which would be equivalent to unique_name being an
        ``AnnotatedString`` and having the ``was_empty`` attribute set to
        ``True``) and their previous and next nodes with an original name. We
        then assign the same unique names for all where the unique names of the
        previous and next nodes with an original name is the same.

        It is yet unclear whether this postprocessing is sufficient but this is
        the place to build upon the postprocessing for further refinement.
        """

        node_context = {}
        for row in rows:
            for idx, entry in enumerate(row):
                # Skip first entry
                if idx == 0:
                    # But make sure rows start with originally named nodes
                    # (i.e. a named source in study or a named sample in assay)
                    if not entry.name:
                        tpl = "Found start node without original name: {}"
                        msg = tpl.format(row[idx].unique_name)
                        raise ParseIsatabException(msg)
                    continue
                # Process nodes without an original name
                if not entry.name:
                    # Find previous originally named node
                    ext = 0
                    while not row[idx - ext - 1].name:
                        ext += 1
                    start_entry = row[idx - ext - 1].unique_name
                    # Find next originally named node
                    # (may stay None, if a bubble is not closed at the end)
                    end_entry = None
                    ext = 0
                    while idx + ext + 1 < len(row) and not row[idx + ext + 1].name:
                        ext += 1
                    if idx + ext + 1 < len(row) and row[idx + ext + 1].name:
                        end_entry = row[idx + ext + 1].unique_name
                    # Compare idx, start and end with previous rows
                    # and perform the change if appropriate
                    key = (idx, start_entry, end_entry)
                    if key in node_context:
                        # TODO: complain if annotations differ?
                        row[idx] = node_context[key]
                    else:
                        node_context[key] = row[idx]
        return rows

    def _construct(self, rows):
        """Construct the ``Assay`` or ``Study`` object."""
        materials = {}
        processes = {}
        arcs = []
        arc_set = set()
        for row in rows:
            for i, entry in enumerate(row):
                # Collect processes and materials
                if isinstance(entry, models.Process):
                    if entry.unique_name in processes and entry != processes[entry.unique_name]:
                        tpl = (
                            "Found processes with same name but different "
                            "annotation:\nprocess 1: {}\nprocess 2: {}"
                        )
                        msg = tpl.format(entry, processes[entry.unique_name])
                        raise ParseIsatabException(msg)
                    processes[entry.unique_name] = entry
                else:
                    assert isinstance(entry, models.Material)
                    if entry.unique_name in materials and entry != materials[entry.unique_name]:
                        tpl = (
                            "Found materials with same name but different "
                            "annotation:\nmaterial 1: {}\nmaterial 2: {}"
                        )
                        msg = tpl.format(entry, materials[entry.unique_name])
                        raise ParseIsatabException(msg)
                    materials[entry.unique_name] = entry
                # Collect arc
                if i > 0:
                    arc = models.Arc(row[i - 1].unique_name, row[i].unique_name)
                    if arc not in arc_set:
                        arc_set.add(arc)
                        arcs.append(arc)
        return self.klass(Path(self.file_name), self.header, materials, processes, tuple(arcs))


class StudyRowReader:
    """Read an ISA-TAB study file (``s_*.txt``) into a tabular/object
    representation.

    This is a more low-level part of the interface.  Please prefer
    using :py:StudyReader: over using this class.
    """

    @classmethod
    def from_stream(
        klass,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        study_id: str,
        input_file: TextIO,
    ):
        """Construct from file-like object"""
        return StudyRowReader(investigation, study, study_id, input_file)

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        study_id: str,
        input_file: TextIO,
    ):
        self.investigation = investigation
        self.study = study
        self.study_id = study_id
        self.input_file = input_file
        self.unique_rows = set()
        self.duplicate_rows = []
        self._reader = csv.reader(input_file, delimiter="\t", quotechar='"')
        self._line = None
        self._read_next_line()
        self.header = self._read_header()

    def _read_header(self):
        """Read first line with header"""
        try:
            line = self._read_next_line()
        except StopIteration as e:
            msg = "Study file has no header!"
            raise ParseIsatabException(msg) from e
        return list(StudyHeaderParser(line, self.study.factors).run())

    def _read_next_line(self):
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        try:
            self._line = next(self._reader)
            while self._line is not None and (not self._line or self._line[0].startswith("#")):
                self._line = next(self._reader)
            # Test and collect row duplicates
            if "\t".join(self._line) in self.unique_rows:
                self.duplicate_rows.append("\t".join(self._line))
            else:
                self.unique_rows.add("\t".join(self._line))
        except StopIteration:
            self._line = None
        return prev_line

    def read(self):
        builder = _StudyRowBuilder(
            self.investigation.ontology_source_refs,
            self.study.protocols,
            self.header,
            self.study_id,
        )
        while True:
            line = self._read_next_line()
            if line:
                yield builder.build(line)
            else:
                break
        # Check if duplicated rows exist
        if self.duplicate_rows:
            lines = "\n{}" * len(self.duplicate_rows)
            tpl = "Found duplicated rows in study {}:{}"
            msg = tpl.format(self.study_id, lines.format(*self.duplicate_rows))
            raise ParseIsatabException(msg)


class StudyReader:
    """Read an ISA-TAB study file (``s_*.txt``) into a ``Study`` object.

    This is the main facade class for reading study objects.  Prefer it
    over using the more low-level code.
    """

    @classmethod
    def from_stream(
        klass,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        study_id: str,
        input_file: TextIO,
    ):
        """Construct from file-like object"""
        return StudyReader(investigation, study, study_id, input_file)

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        study_id: str,
        input_file: TextIO,
    ):
        self.row_reader = StudyRowReader.from_stream(investigation, study, study_id, input_file)
        self.investigation = investigation
        self.study = study
        #: The file used for reading from
        self.input_file = input_file
        #: The header of the ISA study file
        self.header = self.row_reader.header

    def read(self):
        return _AssayAndStudyBuilder(self.input_file.name, self.header, models.Study).build(
            list(self.row_reader.read())
        )


# TODO: extract common parts of {Assay,Study}[Row]Reader into two base classes


class AssayRowReader:
    """Read an ISA-TAB assay file (``a_*.txt``) into a tabular/object
    representation.

    This is a more low-level part of the interface.  Please prefer
    using :py:AssayReader: over using this class.
    """

    @classmethod
    def from_stream(
        klass,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        assay: models.AssayInfo,
        study_id: str,
        assay_id: str,
        input_file: TextIO,
    ):
        """Construct from file-like object"""
        return AssayRowReader(investigation, study, assay, study_id, assay_id, input_file)

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        assay: models.AssayInfo,
        study_id: str,
        assay_id: str,
        input_file: TextIO,
    ):
        self.investigation = investigation
        self.study = study
        self.assay = assay
        self.study_id = study_id
        self.assay_id = assay_id
        self.input_file = input_file
        self.unique_rows = set()
        self.duplicate_rows = []
        self._reader = csv.reader(input_file, delimiter="\t", quotechar='"')
        self._line = None
        self._read_next_line()
        self.header = self._read_header()

    def _read_header(self):
        """Read first line with header"""
        try:
            line = self._read_next_line()
        except StopIteration as e:
            msg = "Assay file has no header!"
            raise ParseIsatabException(msg) from e
        return list(AssayHeaderParser(line, self.study.factors).run())

    def _read_next_line(self):
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        try:
            self._line = next(self._reader)
            while self._line is not None and (not self._line or self._line[0].startswith("#")):
                self._line = next(self._reader)
            # Test and collect row duplicates
            if "\t".join(self._line) in self.unique_rows:
                self.duplicate_rows.append("\t".join(self._line))
            else:
                self.unique_rows.add("\t".join(self._line))
        except StopIteration:
            self._line = None
        return prev_line

    def read(self):
        builder = _AssayRowBuilder(
            self.investigation.ontology_source_refs,
            self.study.protocols,
            self.header,
            self.study_id,
            self.assay_id,
            self.assay,
        )
        while True:
            line = self._read_next_line()
            if line:
                yield builder.build(line)
            else:
                break
        # Check if duplicated rows exist
        if self.duplicate_rows:
            lines = "\n{}" * len(self.duplicate_rows)
            tpl = "Found duplicated rows in assay {} of study {}:{}"
            msg = tpl.format(self.assay_id, self.study_id, lines.format(*self.duplicate_rows))
            raise ParseIsatabException(msg)


class AssayReader:
    """Read an ISA-TAB assay file (``a_*.txt``) into a ``Assay`` object.

    This is the main facade class for reading assay objects.  Prefer it
    over using the more low-level code.
    """

    @classmethod
    def from_stream(
        klass,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        assay: models.AssayInfo,
        study_id: str,
        assay_id: str,
        input_file: TextIO,
    ):
        """Construct from file-like object"""
        return AssayReader(investigation, study, assay, study_id, assay_id, input_file)

    def __init__(
        self,
        investigation: models.InvestigationInfo,
        study: models.StudyInfo,
        assay: models.AssayInfo,
        study_id: str,
        assay_id: str,
        input_file: TextIO,
    ):
        self.row_reader = AssayRowReader.from_stream(
            investigation, study, assay, study_id, assay_id, input_file
        )
        #: The file used for reading from
        self.input_file = input_file
        #: The header of the ISA assay file
        self.header = self.row_reader.header

    def read(self):
        return _AssayAndStudyBuilder(self.input_file.name, self.header, models.Assay).build(
            list(self.row_reader.read())
        )

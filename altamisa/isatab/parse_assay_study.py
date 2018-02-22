# -*- coding: utf-8 -*-
"""This module contains code for the parsing of assay and study files.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, TextIO

from . import models
from ..exceptions import ParseIsatabException
from .headers import ColumnHeader, StudyHeaderParser, AssayHeaderParser


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

# We define constants for the headers in the assay and study files as a typo in
# the code below can then be caught as "unknown identifier" instead of having
# to chase down string mismatches in if/then/else or table lookups.

PROTOCOL_REF = 'protocol_ref'
ASSAY = 'assay'
DATA_NORMALIZATION = 'data_normalization'
DATA_TRANSFORMATION = 'data_transformation'
GEL_ELECTROPHORESIS_ASSAY = 'gel_electrophoresis'
HYBRIDIZATION_ASSAY = 'hybridization'
MS_ASSAY = 'mass_spectometry'
NORMALIZATION = 'normalization'


class _BuilderBase:
    """Base class for builder objects"""

    #: Headers to use for naming
    name_headers = None
    #: Allowed ``column_type``s.
    allowed_column_types = None

    def __init__(
            self,
            ontology_source_refs,
            column_headers: List[ColumnHeader]):
        #: The definition of the ontology source references
        self.ontology_source_refs = ontology_source_refs
        #: The column descriptions to build ``Material`` from.
        self.column_headers = column_headers
        #: The header to use for building names
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
        #: The header for array design reff
        self.array_design_ref_header = None
        #: The header for label type
        self.label_header = None
        #: The header for material type
        self.material_type_header = None
        #: The header for the performer
        self.performer_header = None
        #: The header for the date
        self.date_header = None
        #: The header for the unit
        self.unit_header = None
        #: The header for the scan name
        self.scan_name_header = None
        # Assign column headers to their roles (properties above)
        self._assign_column_headers()

    def _assign_column_headers(self):
        # Record the last column header that is a primary annotation (e.g.,
        # Characteristics[*] is but "Term Source REF" is not.
        prev = None
        for no, header in enumerate(self.column_headers):
            if (header.column_type not in self.name_headers and
                    header.column_type not in self.allowed_column_types):
                tpl = 'Invalid column type occured {} not in {}'
                msg = tpl.format(header.column_type, self.allowed_column_types)
                raise ParseIsatabException(msg)
            is_secondary = False
            if no == 0:  # short-circuit name header
                assert header.column_type in self.name_headers
                self.name_header = header
            elif header.column_type == 'Characteristics':
                self.characteristic_headers.append(header)
            elif header.column_type == 'Comment':
                self.comment_headers.append(header)
            elif header.column_type == 'Factor Value':
                self.factor_value_headers.append(header)
            elif header.column_type == 'Parameter Value':
                self.parameter_value_headers.append(header)
            elif header.column_type == 'Material Type':
                if self.material_type_header:
                    tpl = ('Seen "Material Type" header for same entity in '
                           'col {}')
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.material_type_header = header
            elif header.column_type == 'Array Design REF':
                if self.array_design_ref_header:
                    tpl = ('Seen "Array Design REF" header for same entity '
                           'in col {}')
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.array_design_ref_header = header
            elif header.column_type == 'Label':
                if self.label_header:
                    tpl = 'Seen "Label" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.label_header = header
            elif header.column_type == 'Date':
                if self.date_header:
                    tpl = 'Seen "Date" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.date_header = header
            elif header.column_type == 'Performer':
                if self.performer_header:
                    tpl = 'Seen "Performer" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.performer_header = header
            elif header.column_type == 'Term Source REF':
                # Guard against misuse / errors
                if not prev:
                    tpl = ('No primary annotation to annotate with term in '
                           'col {}')
                elif prev.term_source_ref_header:
                    tpl = ('Seen "Term Source REF" header for same entity '
                           'in col {}')
                else:
                    tpl = None
                if tpl:
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    # The previous non-secondary header is annotated with an
                    # ontology term.
                    prev.term_source_ref_header = header
                    is_secondary = True
            elif header.column_type == 'Unit':
                if prev.term_source_ref_header:
                    tpl = 'Seen "Unit" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    # The previous non-secondary header is annotated with a
                    # unit.
                    prev.unit_header = header
                    is_secondary = True
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

    def _build_freetext_or_term_ref(
            self,
            header,
            line: List[str]) -> models.FreeTextOrTermRef:
        if not header or not line[header.col_no]:
            return None
        elif header.term_source_ref_header:
            header2 = header.term_source_ref_header
            name = line[header.col_no]
            ontology_name = line[header2.col_no]
            accession = line[header2.col_no + 1]
            ontology = self.ontology_source_refs[ontology_name]
            return models.OntologyTermRef(
                name, accession, ontology_name, ontology)
        else:
            return line[header.col_no]


class _MaterialBuilder(_BuilderBase):
    """Helper class to construct a ``Material`` object from a line"""

    type_ = models.MATERIAL

    name_headers = (
        # Material
        'Extract Name', 'Labeled Extract Name', 'Material Name',
        'Source Name', 'Sample Name',
        # Data
        'Array Data File', 'Array Data Matrix File',
        'Derived Array Data File', 'Derived Array Data Matrix File',
        'Derived Data File', 'Derived Spectral Data File',
        'Raw Data File', 'Raw Spectral Data File'
        )

    allowed_column_types = (
        # Primary annotations (not parametrized)
        'Material Type',
        # Primary annotations (parametrized)
        'Characteristics', 'Comment', 'Factor Value',
        # Secondary annotations
        'Label', 'Term Source REF', 'Unit')

    def build(self, line: List[str]) -> models.Material:
        """Build and return ``Material`` from TSV file line."""
        # First, build the individual components
        type_ = self.name_header.column_type.replace(' Name', '')
        name = line[self.name_header.col_no]
        label = None
        if self.label_header:
            label = line[self.label_header.col_no]
        characteristics = tuple(
            self._build_complex(hdr, line, models.Characteristics)
            for hdr in self.characteristic_headers)
        comments = tuple(
            self._build_complex(hdr, line, models.Comment)
            for hdr in self.comment_headers)
        factor_values = tuple(
            self._build_complex(hdr, line, models.FactorValue)
            for hdr in self.factor_value_headers)
        material_type = self._build_freetext_or_term_ref(
            self.material_type_header, line)
        # Then, constructing ``Material`` is easy
        return models.Material(
            type_, name, label, characteristics, comments,
            factor_values, material_type)


class _SourceBuilder(_MaterialBuilder):
    """Specialization of ``_MaterialBuilder`` to build source ``Material``
    objects."""

    type_ = models.SOURCE


class _SampleBuilder(_MaterialBuilder):
    """Specialization of ``_MaterialBuilder`` to build source ``Sample``
    objects."""

    type_ = models.SAMPLE


class _ExtractBuilder(_MaterialBuilder):
    """Specialization of ``_MaterialBuilder`` to build source ``Extract``
    objects."""

    type_ = models.EXTRACT


class _LabeledExtractBuilder(_MaterialBuilder):
    """Specialization of ``_MaterialBuilder`` to build source
    ``Labeled Extract`` objects."""

    type_ = models.LABELED_EXTRACT


class _DataBuilder(_MaterialBuilder):
    """Base class for data builders"""


class _ArrayDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``ArrayData``
    objects."""

    type_ = models.ARRAY_DATA_FILE


class _ArrayDataMatrixBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``ArrayDataMatrix``
    objects."""

    type_ = models.ARRAY_DATA_MATRIX_FILE


class _DerivedArrayDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedArrayData``
    objects."""

    type_ = models.DERIVED_ARRAY_DATA_FILE


class _DerivedArrayMatrixDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source
    ``DerivedArrayMatrixData`` objects."""

    type_ = models.DERIVED_ARRAY_MATRIX_DATA_FILE


class _DerivedDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedData``
    objects."""

    type_ = models.DERIVED_DATA_FILE


class _DerivedSpectralDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedData``
    objects."""

    type_ = models.DERIVED_SPECTRAL_DATA_FILE


class _RawDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedSpectralData``
    objects."""

    type_ = models.RAW_DATA_FILE


class _RawSpectralDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedSpectralData``
    objects."""

    type_ = models.RAW_SPECTRAL_DATA_FILE


class _ProcessBuilder(_BuilderBase):
    """Helper class to construct ``Process`` objects."""

    name_headers = (
        'Protocol REF',
        'Normalization Name',
        'Data Normalization Name',
        'Data Transformation Name',
        'Gel Electrophoresis Name',
        'Hybridization Assay Name',
        'MS Assay Name',
    )

    allowed_column_types = (
        # Primary annotations (not parametrized)
        'Performer', 'Date', 'Array Design REF', 'Scan Name',
        # Primary annotations (parametrized)
        'Parameter Value', 'Characteristics', 'Comment',
        # Secondary annotations
        'Term Source REF', 'Unit')

    def build(self, line: List[str]) -> models.Process:
        """Build and return ``Process`` from CSV file."""
        # First, build the individual components
        type_ = self.name_header.column_type.replace(' Name', '')
        name = line[self.name_header.col_no]
        array_design_ref = None
        performer = None
        process_date = None
        scan_name = None
        if self.array_design_ref_header:
            array_design_ref = line[self.array_design_ref_header.col_no]
        if self.performer_header:
            performer = line[self.performer_header.col_no]
        if self.date_header:
            process_date = datetime.strptime(
                line[self.date_header.col_no], '%Y-%m-%d').date()
        if self.scan_name_header:
            scan_name = datetime.strptime(
                line[self.scan_name_header.col_no], '%Y-%m-%d').date()
        characteristics = tuple(
            self._build_complex(hdr, line, models.Characteristics)
            for hdr in self.characteristic_headers)
        comments = tuple(
            self._build_complex(hdr, line, models.Comment)
            for hdr in self.comment_headers)
        parameter_values = tuple(
            self._build_complex(hdr, line, models.ParameterValue)
            for hdr in self.parameter_value_headers)
        # Then, constructing ``Process`` is easy
        return models.Process(
            type_, name, array_design_ref, process_date, performer,
            scan_name, characteristics, comments, parameter_values)


class _ProtocolRefBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Protocol
    ``Process`` objects."""

    type_ = models.PROTOCOL_REF


class _AssayBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Assay
    ``Process`` objects."""

    type_ = models.ASSAY


class _DataNormalizationBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Data Normalization
    ``Process`` objects."""

    type_ = models.DATA_NORMALIZATION


class _DataTransformationBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Data Transformation
    ``Process`` objects."""

    type_ = models.DATA_TRANSFORMATION


class _GelElectrophoresisAssayBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Gel Electrophoresis Assay
    ``Process`` objects."""

    type_ = models.GEL_ELECTROPHORESIS_ASSAY


class _HybridizationAssayBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Hybridization Assay
    ``Process`` objects."""

    type_ = models.HYBRIDIZATION_ASSAY


class _MsAssayBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build MS Assay
    ``Process`` objects."""

    type_ = models.MS_ASSAY


class _NormalizationBuilder(_ProcessBuilder):
    """Specialization of ``_ProcessBuilder`` to build Normalization
    ``Process`` objects."""

    type_ = models.NORMALIZATION


class _RowBuilderBase:
    """Base class for row builders from study and assay files"""

    #: Registry of column header to node builder
    node_builders = None

    def __init__(self, ontology_source_refs, header: List[ColumnHeader]):
        self.ontology_source_refs = ontology_source_refs
        self.header = header
        self._builders = list(self._make_builders())

    def _make_builders(self):
        """Construct the builder objects for the objects"""
        breaks = list(self._make_breaks())
        for start, end in zip(breaks, breaks[1:]):
            klass = self.node_builders[self.header[start].column_type]
            yield klass(self.ontology_source_refs, self.header[start:end])

    def _make_breaks(self):
        """Build indices to break the columns at."""
        for i, col_hdr in enumerate(self.header):
            if col_hdr.column_type in self.node_builders:
                yield i
        yield len(self.header)  # index to end of list

    def build(self, line):
        return [b.build(line) for b in self._builders]


class _StudyRowBuilder(_RowBuilderBase):
    """Build a row from an ISA-TAB study file."""

    node_builders = {
        # Material node builders
        'Source Name': _SourceBuilder,
        'Sample Name': _SampleBuilder,
        # Process node builders
        'Protocol REF': _ProcessBuilder,
    }


class _AssayRowBuilder(_RowBuilderBase):
    """Build a row from an ISA-TAB assay file."""

    node_builders = {
        # Material node builders
        'Sample Name': _SampleBuilder,
        'Extract Name': _ExtractBuilder,
        'Labeled Extract Name': _LabeledExtractBuilder,
        # Data node builders
        'Array Data File': _ArrayDataBuilder,
        'Array Data Matrix File': _ArrayDataMatrixBuilder,
        'Derived Array Data File': _DerivedArrayDataBuilder,
        'Derived Array Data Matrix File': _DerivedArrayMatrixDataBuilder,
        'Derived Data File': _DerivedDataBuilder,
        'Derived Spectral Data File': _DerivedSpectralDataBuilder,
        'Raw Data File': _RawDataBuilder,
        'Raw Spectral Data File': _RawSpectralDataBuilder,
        # Process node builders
        'Assay Name': _AssayBuilder,
        'Data Normalization Name': _DataNormalizationBuilder,
        'Data Transformation Name': _DataTransformationBuilder,
        'Gel Electrophoresis Assay Name': _GelElectrophoresisAssayBuilder,
        'Hybridization Assay Name': _HybridizationAssayBuilder,
        'MS Assay Name': _MsAssayBuilder,
        'Normalization Name': _NormalizationBuilder,
        'Protocol REF': _ProtocolRefBuilder,
    }


def _build_study_assay(file_name, rows, klass):
    """Helper for building Study and Assay objects"""
    #: TODO: this is bogus
    row_len = None
    materials = {}
    arcs = []
    arc_set = set()
    for row in rows:
        if row_len is None:
            row_len = len(row)
            if row_len % 2 != 1:
                tpl = 'Even number of entities in row (file {}): {}'
                msg = tpl.format(file_name, len(row))
                raise ParseIsatabException(msg)
        else:
            if not row_len == len(row):
                tpl = ('Inconsistent number of entities in row (file {}): '
                       '{} vs {}')
                msg = tpl.format(file_name, row_len, len(row))
                raise ParseIsatabException(msg)
        assert len(row) % 2 == 1
        # Create materials
        for i in range(0, len(row), 2):
            material = row[i]
            if material.name not in materials:
                materials[material.name] = material
        # Create arcs
        for i in range(1, len(row), 2):
            arc = models.ProcessArc(row[i - 1].name, row[i + 1].name, row[i])
            if arc not in arc_set:
                arc_set.add(arc)
                arcs.append(arc)
    return klass(Path(file_name), materials, tuple(arcs))


class StudyReader:
    """Read an ISA-TAB study file (``s_*.txt``) into a tabular/object
    representation.
    """

    @classmethod
    def from_stream(
            klass,
            investigation: models.Investigation,
            input_file: TextIO):
        """Construct from file-like object"""
        return StudyReader(investigation, input_file)

    def __init__(
            self,
            investigation: models.Investigation,
            input_file: TextIO):
        self.investigation = investigation
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
            self._line = self.input_file.next()
        return prev_line

    def read(self):
        try:
            line = self._read_next_line()
        except StopIteration:
            msg = 'Study file has no header!'
            raise ParseIsatabException(msg)
        self.header = list(StudyHeaderParser(line).run())
        # import sys, pprint
        # print('STUDY HEADER', file=sys.stderr)
        # pprint.pprint(self.header, stream=sys.stderr)
        # print('-- END: STUDY HEADER', file=sys.stderr)
        builder = _StudyRowBuilder(
            self.models.ontology_source_refs,
            self.header)
        rows = []
        while True:
            try:
                line = self._read_next_line()
            except StopIteration:
                break
            # import sys, pprint
            # print('LINE', file=sys.stderr)
            # pprint.pprint(line, stream=sys.stderr)
            # print('-- END: LINE', file=sys.stderr)
            row = builder.build(line)
            # print('ROW', file=sys.stderr)
            # pprint.pprint(row, stream=sys.stderr)
            # print('-- END: ROW', file=sys.stderr)
            rows.append(row)
        return _build_study_assay(
            self.input_file.name, rows, models.Study)


class AssayReader:
    """Read an ISA-TAB assay file (``a_*.txt``) into a tabular/object
    representation.
    """

    @classmethod
    def from_stream(
            klass,
            investigation: models.Investigation,
            input_file: TextIO):
        """Construct from file-like object"""
        return AssayReader(investigation, input_file)

    def __init__(
            self,
            investigation: models.Investigation,
            input_file: TextIO):
        self.investigation = investigation
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

    def read(self):
        try:
            line = self._read_next_line()
        except StopIteration:
            msg = 'Assay file has no header!'
            raise ParseIsatabException(msg)
        self.header = list(AssayHeaderParser(line).run())
        # import sys, pprint
        # print('ASSAY HEADER', file=sys.stderr)
        # pprint.pprint(self.header, stream=sys.stderr)
        # print('-- END: ASSAY HEADER', file=sys.stderr)
        builder = _AssayRowBuilder(
            self.models.ontology_source_refs,
            self.header)
        rows = []
        while True:
            try:
                line = self._read_next_line()
            except StopIteration:
                break
            # import sys, pprint
            # print('LINE', file=sys.stderr)
            # pprint.pprint(line, stream=sys.stderr)
            # print('-- END: LINE', file=sys.stderr)
            row = builder.build(line)
            # print('ROW', file=sys.stderr)
            # pprint.pprint(row, stream=sys.stderr)
            # print('-- END: ROW', file=sys.stderr)
            rows.append(row)
        return _build_study_assay(
            self.input_file.name, rows, models.Assay)

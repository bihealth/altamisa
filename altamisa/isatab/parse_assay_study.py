# -*- coding: utf-8 -*-
"""This module contains code for the parsing of assay and study files.
"""

# TODO: validate whether protocol is known in investigation

import csv
from datetime import datetime
from pathlib import Path
from typing import List, TextIO

from . import models
from ..exceptions import ParseIsatabException
from .headers import ColumnHeader, StudyHeaderParser, AssayHeaderParser


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Used for marking anonymous/unnamed Processes
TOKEN_ANONYMOUS = 'Anonymous'
#: Used for marking empty/unnamed Data
TOKEN_EMPTY = 'Empty'

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

#: Header values indicating a material name.
_MATERIAL_NAME_HEADERS = (
    # Material
    'Extract Name',
    'Labeled Extract Name',
    'Source Name',
    'Sample Name',
    # Data
    'Array Data File',
    'Array Data Matrix File',
    'Derived Array Data File',
    'Derived Array Data Matrix File',
    'Derived Data File',
    'Derived Spectral Data File',
    'Metabolite Assignment File',
    'Peptide Assignment File',
    'Post Translational Modification Assignment File',
    'Protein Assignment File',
    'Raw Data File',
    'Raw Spectral Data File')

#: Header values indicating a process name.
_PROCESS_NAME_HEADERS = (
    'Assay Name',
    'Protocol REF',
    'Normalization Name',
    'Data Normalization Name',
    'Data Transformation Name',
    'Gel Electrophoresis Name',
    'Hybridization Assay Name',
    'MS Assay Name')


class _NodeBuilderBase:
    """Base class for Material and Process builder objects"""

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
        #: The header for the scan name
        self.scan_name_header = None
        #: Current counter value
        self.counter_value = 0
        # Assign column headers to their roles (properties above)
        self._assign_column_headers()

    def _next_counter(self):
        """Increment counter value and return"""
        self.counter_value += 1
        return self.counter_value

    def _assign_column_headers(self):
        # Record the last column header that is a primary annotation (e.g.,
        # "Characteristics[*]" is but "Term Source REF" is not.
        prev = None
        # Interpret the full sequence of column headers.
        for no, header in enumerate(self.column_headers):
            if (header.column_type not in self.name_headers and
                    header.column_type not in self.allowed_column_types):
                tpl = 'Invalid column type occured "{}" not in {}'
                msg = tpl.format(header.column_type, self.allowed_column_types)
                raise ParseIsatabException(msg)
            # Most headers are not secondary, so make this the default state.
            is_secondary = False
            if header.column_type == 'Protocol REF':
                assert not self.protocol_ref_header
                self.protocol_ref_header = header
            elif header.column_type in self.name_headers:
                assert not self.name_header
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
                if self.extract_label_header:
                    tpl = 'Seen "Label" header for same entity in col {}'
                    msg = tpl.format(header.col_no)
                    raise ParseIsatabException(msg)
                else:
                    self.extract_label_header = header
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
        if not header:
            return None
        elif header.term_source_ref_header:
            header2 = header.term_source_ref_header
            name = line[header.col_no]
            ontology_name = line[header2.col_no]
            accession = line[header2.col_no + 1]
            return models.OntologyTermRef(
                name, accession, ontology_name, self.ontology_source_refs)
        else:
            return line[header.col_no]


class _MaterialBuilder(_NodeBuilderBase):
    """Helper class to construct a ``Material`` object from a line"""

    type_ = models.MATERIAL

    name_headers = _MATERIAL_NAME_HEADERS

    allowed_column_types = (
        # Primary annotations (not parametrized)
        'Material Type',
        # Primary annotations (parametrized)
        'Characteristics', 'Comment', 'Factor Value',
        # Secondary annotations
        'Label', 'Term Source REF', 'Unit')

    def build(self, line: List[str]) -> models.Material:
        """Build and return ``Material`` from TSV file line."""
        counter_value = self._next_counter()
        # First, build the individual components
        assert self.name_header or self.protocol_ref_header
        type_ = self.name_header.column_type
        if line[self.name_header.col_no]:
            # make material/data names unique by column
            if self.name_header.column_type == "Source Name":
                unique_name = '{}-{}'.format(
                    "source",
                    line[self.name_header.col_no])
            elif self.name_header.column_type == "Sample Name":
                # use static column identifier "sample-", since the same
                # samples occur in different columns in study and assay
                unique_name = '{}-{}'.format(
                    "sample",
                    line[self.name_header.col_no])
            else:
                # anything else gets the column id
                unique_name = '{}-COL{}'.format(
                    line[self.name_header.col_no],
                    self.name_header.col_no + 1)
        else:
            name_val = '{} {}-{}-{}'.format(
                TOKEN_EMPTY, self.name_header.column_type,
                self.name_header.col_no + 1, counter_value)
            unique_name = models.AnnotatedStr(name_val, was_empty=True)
        extract_label = None
        if self.extract_label_header:
            extract_label = line[self.extract_label_header.col_no]
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
            type_, unique_name, extract_label, characteristics, comments,
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


class _MetaboliteAssignmentFileBuilder(_DataBuilder):

    type_ = models.METABOLITE_ASSIGNMENT_FILE


class _PeptideAssignmentFileBuilder(_DataBuilder):

    type_ = models.PEPTIDE_ASSIGNMENT_FILE


class _ProteinAssignmentFileBuilder(_DataBuilder):

    type_ = models.PROTEIN_ASSIGNMENT_FILE


class _PostTranslationalModificationAssignmentFileBuilder(_DataBuilder):

    type_ = models.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE


class _RawDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedSpectralData``
    objects."""

    type_ = models.RAW_DATA_FILE


class _RawSpectralDataBuilder(_DataBuilder):
    """Specialization of ``_DataBuilder`` to build source ``DerivedSpectralData``
    objects."""

    type_ = models.RAW_SPECTRAL_DATA_FILE


class _ProcessBuilder(_NodeBuilderBase):
    """Helper class to construct ``Process`` objects."""

    name_headers = _PROCESS_NAME_HEADERS

    allowed_column_types = (
        # Primary annotations (not parametrized)
        'Performer', 'Date', 'Array Design REF', 'Scan Name',
        # Primary annotations (parametrized)
        'Parameter Value', 'Characteristics', 'Comment',
        # Secondary annotations
        'Term Source REF', 'Unit')

    def build(self, line: List[str]) -> models.Process:
        """Build and return ``Process`` from CSV file."""
        # First, build the individual attributes of ``Process``
        protocol_ref, unique_name = self._build_protocol_ref_and_name(line)
        if self.date_header and line[self.date_header.col_no]:
            try:
                date = datetime.strptime(
                        line[self.date_header.col_no], '%Y-%m-%d').date()
            except ValueError:
                tpl = 'Invalid ISO8601 date "{}"'
                msg = tpl.format(line[self.date_header.col_no])
                raise ParseIsatabException(msg)
        else:
            date = None
        if self.performer_header:
            performer = line[self.performer_header.col_no]
        else:
            performer = None
        comments = tuple(
            self._build_complex(hdr, line, models.Comment)
            for hdr in self.comment_headers)
        parameter_values = tuple(
            self._build_complex(hdr, line, models.ParameterValue)
            for hdr in self.parameter_value_headers)
        if self.array_design_ref_header:
            array_design_ref = line[self.array_design_ref_header.col_no]
        else:
            array_design_ref = None
        if self.scan_name_header:
            scan_name = datetime.strptime(
                line[self.scan_name_header.col_no], '%Y-%m-%d').date()
        else:
            scan_name = None
        # Then, constructing ``Process`` is easy
        return models.Process(
            protocol_ref, unique_name, date, performer, parameter_values,
            comments, array_design_ref, scan_name)

    def _build_protocol_ref_and_name(self, line: List[str]):
        # At least one of these headers has to be specified
        assert self.name_header or self.protocol_ref_header
        # Perform case distinction on which case is actually true
        counter_value = self._next_counter()
        if not self.name_header:
            # Name header is given but value is empty, will use auto-generated
            # value.
            protocol_ref = line[self.protocol_ref_header.col_no]
            unique_name = '{}-{}-{}'.format(
                protocol_ref, self.protocol_ref_header.col_no + 1,
                counter_value)
        elif not self.protocol_ref_header:
            protocol_ref = 'UNKNOWN'
            if line[self.name_header.col_no]:
                unique_name = line[self.name_header.col_no]
            else:  # empty!
                name_val = '{} {}-{}-{}'.format(
                    TOKEN_ANONYMOUS,
                    self.name_header.column_type.replace(' Name', ''),
                    self.name_header.col_no + 1, counter_value)
                unique_name = models.AnnotatedStr(name_val, was_empty=True)
        else:  # both are given
            protocol_ref = line[self.protocol_ref_header.col_no]
            if line[self.name_header.col_no]:
                unique_name = line[self.name_header.col_no]
            else:
                unique_name = '{}-{}'.format(protocol_ref, counter_value)
        return protocol_ref, unique_name


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
            if col_hdr.column_type in _MATERIAL_NAME_HEADERS:
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
        'Metabolite Assignment File': _MetaboliteAssignmentFileBuilder,
        'Peptide Assignment File': _PeptideAssignmentFileBuilder,
        'Post Translational Modification Assignment File':
            _PostTranslationalModificationAssignmentFileBuilder,
        'Protein Assignment File': _ProteinAssignmentFileBuilder,
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


def _build_study_assay(file_name, header, rows, klass):
    """Helper for building ``Study`` and ``Assay`` objects.
    """
    materials = {}
    processes = {}
    arcs = []
    arc_set = set()
    for row in rows:
        for i, entry in enumerate(row):
            # Collect entry and materials
            if isinstance(entry, models.Process):
                processes[entry.unique_name] = entry
            else:
                assert isinstance(entry, models.Material)
                materials[entry.unique_name] = entry
            # Collect arc
            if i > 0:
                arc = models.Arc(row[i - 1].unique_name, row[i].unique_name)
                if arc not in arc_set:
                    arc_set.add(arc)
                    arcs.append(arc)
    return klass(Path(file_name), header, materials, processes, tuple(arcs))


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
            study_id: str,
            input_file: TextIO):
        """Construct from file-like object"""
        return StudyRowReader(investigation, study_id, input_file)

    def __init__(
            self,
            investigation: models.InvestigationInfo,
            study_id: str,
            input_file: TextIO):
        self.investigation = investigation
        self.study_id = study_id
        self.input_file = input_file
        self._reader = csv.reader(input_file, delimiter='\t', quotechar='"')
        self._line = None
        self._read_next_line()
        self.header = self._read_header()

    def _read_header(self):
        """Read first line with header"""
        try:
            line = self._read_next_line()
        except StopIteration:
            msg = 'Study file has no header!'
            raise ParseIsatabException(msg)
        return list(StudyHeaderParser(line).run())

    def _read_next_line(self):
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        try:
            self._line = next(self._reader)
            while self._line is not None and (
                    not self._line or self._line[0].startswith('#')):
                self._line = self.input_file.next()
        except StopIteration:
            self._line = None
        return prev_line

    def read(self):
        builder = _StudyRowBuilder(
            self.investigation.ontology_source_refs,
            self.header)
        while True:
            line = self._read_next_line()
            if line:
                yield builder.build(line)
            else:
                break


class StudyReader:
    """Read an ISA-TAB study file (``s_*.txt``) into a ``Study`` object.

    This is the main facade class for reading study objects.  Prefer it
    over using the more low-level code.
    """

    @classmethod
    def from_stream(
            klass,
            investigation: models.InvestigationInfo,
            study_id: str,
            input_file: TextIO):
        """Construct from file-like object"""
        return StudyReader(investigation, study_id, input_file)

    def __init__(
            self,
            investigation: models.InvestigationInfo,
            study_id: str,
            input_file: TextIO):
        self.row_reader = StudyRowReader.from_stream(
            investigation, study_id, input_file)
        self.investigation = investigation
        #: The file used for reading from
        self.input_file = input_file
        #: The header of the ISA study file
        self.header = self.row_reader.header

    def read(self):
        return _build_study_assay(
            self.input_file.name, self.header, list(self.row_reader.read()),
            models.Study)


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
            study_id: str,
            assay_id: str,
            input_file: TextIO):
        """Construct from file-like object"""
        return AssayRowReader(investigation, study_id, assay_id, input_file)

    def __init__(
            self,
            investigation: models.InvestigationInfo,
            study_id: str,
            assay_id: str,
            input_file: TextIO):
        self.investigation = investigation
        self.study_id = study_id
        self.assay_id = assay_id
        self.input_file = input_file
        self._reader = csv.reader(input_file, delimiter='\t', quotechar='"')
        self._line = None
        self._read_next_line()
        self.header = self._read_header()

    def _read_header(self):
        """Read first line with header"""
        try:
            line = self._read_next_line()
        except StopIteration:
            msg = 'Study file has no header!'
            raise ParseIsatabException(msg)
        return list(AssayHeaderParser(line).run())

    def _read_next_line(self):
        """Read next line, skipping comments starting with ``'#'``."""
        prev_line = self._line
        try:
            self._line = next(self._reader)
            while self._line is not None and (
                    not self._line or self._line[0].startswith('#')):
                self._line = self.input_file.next()
        except StopIteration:
            self._line = None
        return prev_line

    def read(self):
        builder = _AssayRowBuilder(
            self.investigation.ontology_source_refs,
            self.header)
        while True:
            line = self._read_next_line()
            if line:
                yield builder.build(line)
            else:
                break


class AssayReader:
    """Read an ISA-TAB assay file (``a_*.txt``) into a ``Assay`` object.

    This is the main facade class for reading assay objects.  Prefer it
    over using the more low-level code.
    """

    @classmethod
    def from_stream(
            klass,
            investigation: models.InvestigationInfo,
            study_id: str,
            assay_id: str,
            input_file: TextIO):
        """Construct from file-like object"""
        return AssayReader(investigation, study_id, assay_id, input_file)

    def __init__(
            self,
            investigation: models.InvestigationInfo,
            study_id: str,
            assay_id: str,
            input_file: TextIO):
        self.row_reader = AssayRowReader.from_stream(
            investigation, study_id, assay_id, input_file)
        self.investigation = investigation
        #: The file used for reading from
        self.input_file = input_file
        #: The header of the ISA assay file
        self.header = self.row_reader.header

    def read(self):
        return _build_study_assay(
            self.input_file.name, self.header, list(self.row_reader.read()),
            models.Assay)

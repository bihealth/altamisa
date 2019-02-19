# -*- coding: utf-8 -*-
"""This module contains code for the representation of headers from study and
assay files and parsing thereof.
"""

from __future__ import generator_stop

from typing import Iterator
from ..exceptions import ParseIsatabException


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class ColumnHeader:
    """Column header in a study or assay file"""

    def __init__(self, column_type, col_no, span):
        #: The type of this header
        self.column_type = column_type
        #: The column number this header refers to
        self.col_no = col_no
        #: Number of columns this header spans
        self.span = span
        #: Link to the TermSourceRefHeader to use
        self.term_source_ref_header = None
        #: Link to the UnitHeader to use
        self.unit_header = None

    def __str__(self):
        tpl = 'ColumnHeader(column_type={}, col_no={}, span={})'
        return tpl.format(*map(repr, (
            self.column_type, self.col_no, self.span)))

    def __repr__(self):
        return str(self)


class SimpleColumnHeader(ColumnHeader):
    """Base class for simple column headers."""

    #: The value to use for the ``type`` argument.
    column_type = None

    def __init__(self, col_no):
        super().__init__(self.column_type, col_no, 1)


class SourceHeader(SimpleColumnHeader):
    """Source header in a study or assay"""

    column_type = 'Source Name'


class ExtractHeader(SimpleColumnHeader):
    """Extract header in a study or assay"""

    column_type = 'Extract Name'


class LabeledExtractHeader(SimpleColumnHeader):
    """Labeled Extract header in a study or assay"""

    column_type = 'Labeled Extract Name'


class ArrayDataFileHeader(SimpleColumnHeader):
    """ArrayData header in a study or assay"""

    column_type = 'Array Data File'


class ArrayDataMatrixFileHeader(SimpleColumnHeader):
    """ArrayData Matrix File header in a study or assay"""

    column_type = 'Array Data Matrix File'


class DerivedArrayDataFileHeader(SimpleColumnHeader):
    """DerivedArrayData header in a study or assay"""

    column_type = 'Derived Array Data File'


class DerivedDataFileHeader(SimpleColumnHeader):
    """Derived Data File header in a study or assay"""

    column_type = 'Derived Data File'


class DerivedArrayDataMatrixFileHeader(SimpleColumnHeader):
    """DerivedArrayData header in a study or assay"""

    column_type = 'Derived Array Data Matrix File'


class DerivedSpectralDataFileHeader(SimpleColumnHeader):
    """DerivedSpectralData header in a study or assay"""

    column_type = 'Derived Spectral Data File'


class PeptideAssignmentFileHeader(SimpleColumnHeader):
    """PeptideAssignment header in a study or assay"""

    column_type = 'Peptide Assignment File'


class PostTranslationalModificationAssignmentFileHeader(SimpleColumnHeader):
    """PostTranslationalModificationAssignment header in a study or assay"""

    column_type = 'Post Translational Modification Assignment File'


class ProteinAssignmentFileHeader(SimpleColumnHeader):
    """ProteinAssignment header in a study or assay"""

    column_type = 'Protein Assignment File'


class RawDataFileHeader(SimpleColumnHeader):
    """Raw Data header in a study or assay"""

    column_type = 'Raw Data File'


class RawSpectralDataFileHeader(SimpleColumnHeader):
    """Raw Spectral Data header in a study or assay"""

    column_type = 'Raw Spectral Data File'


class AssayNameHeader(SimpleColumnHeader):
    """Assay Name header in a study or assay"""

    column_type = 'Assay Name'


class DataNormalizationNameHeader(SimpleColumnHeader):
    """Data Normalization Name header in a study or assay"""

    column_type = 'Data Normalization Name'


class NormalizationNameHeader(SimpleColumnHeader):
    """Normalization Name header in a study or assay"""

    column_type = 'Normalization Name'


class DataTransformationNameHeader(SimpleColumnHeader):
    """DataTransformationName header in a study or assay"""

    column_type = 'Data Transformation Name'


class GelElectrophoresisAssayNameHeader(SimpleColumnHeader):
    """GelElectrophoresisAssayName header in a study or assay"""

    column_type = 'GelElectrophoresis Assay Name'


class HybridizationAssayNameHeader(SimpleColumnHeader):
    """HybridizationAssayName header in a study or assay"""

    column_type = 'Hybridization Assay Name'


class MsAssayNameHeader(SimpleColumnHeader):
    """MsAssayName header in a study or assay"""

    column_type = 'MS Assay Name'


class ArrayDesignFileHeader(SimpleColumnHeader):
    """ArrayDesignFile header in a study or assay"""

    column_type = 'Array Design File'


class ArrayDesignRefHeader(SimpleColumnHeader):
    """ArrayDesignRef header in a study or assay"""

    column_type = 'Array Design REF'


class FirstDimensionHeader(SimpleColumnHeader):
    """First Dimension header in a study or assay"""

    column_type = 'First Dimension'


class MaterialTypeHeader(SimpleColumnHeader):
    """Material Type header in a study or assay"""

    column_type = 'Material Type'


class LabelHeader(SimpleColumnHeader):
    """Material Type header in a study or assay"""

    column_type = 'Label'


class SecondDimensionHeader(SimpleColumnHeader):
    """SecondDimension header in a study or assay"""

    column_type = 'Second Dimension'


class ScanNameHeader(SimpleColumnHeader):
    """ScanName header in a study or assay"""

    column_type = 'Scan Name'


class SpotPickingFileHeader(SimpleColumnHeader):
    """SpotPickingFile header in a study or assay"""

    column_type = 'Spot Picking File'


class SampleHeader(SimpleColumnHeader):
    """Sample header in a study or assay"""

    column_type = 'Sample Name'


class ProtocolRefHeader(SimpleColumnHeader):
    """Protocol REF header in a study or assay"""

    column_type = 'Protocol REF'


class PerformerHeader(SimpleColumnHeader):
    """Performer header in a study or assay"""

    column_type = 'Performer'


class UnitHeader(SimpleColumnHeader):
    """Unit annotation header in a study or assay"""

    column_type = 'Unit'


class DateHeader(SimpleColumnHeader):
    """Date annotation header in a study or assay"""

    column_type = 'Date'


class LabeledColumnHeader(ColumnHeader):
    """Base class for labeled column headers."""

    #: The value to use for the ``type`` argument.
    column_type = None

    def __init__(self, col_no, label):
        super().__init__(self.column_type, col_no, 1)
        self.label = label

    def __str__(self):
        tpl = ('LabeledColumnHeader('
               'column_type={}, col_no={}, span={}, label={})')
        return tpl.format(*map(repr, (
            self.column_type, self.col_no, self.span, self.label)))


class CommentHeader(LabeledColumnHeader):
    """Comment header in a study or assay"""

    column_type = 'Comment'


class CharacteristicsHeader(LabeledColumnHeader):
    """Protocol Characteristics[*] header in a study or assay"""

    column_type = 'Characteristics'


class FactorValueHeader(LabeledColumnHeader):
    """Protocol ``Factor Value[*]`` header in a study or assay"""

    column_type = 'Factor Value'


class ParameterValueHeader(LabeledColumnHeader):
    """Protocol ``Parameter Value[*]`` header in a study or assay"""

    column_type = 'Parameter Value'


class TermRefAnnotationHeader(ColumnHeader):
    """Term reference annotation header"""

    def __init__(self, col_no):
        super().__init__('Term Source REF', col_no, 2)


class HeaderParserBase:
    """Helper base class for parsing a header from a study or assay file."""

    #: Names of the allowed headers
    allowed_headers = None

    #: Headers that are mapped to ``SimpleColumnHeader``s
    simple_headers = {
        # Material headers
        'Sample Name': SampleHeader,
        'Source Name': SourceHeader,
        'Extract Name': ExtractHeader,
        'Labeled Extract Name': LabeledExtractHeader,
        # Data headers
        'Array Data File': ArrayDataFileHeader,
        'Array Data Matrix File': ArrayDataMatrixFileHeader,
        'Derived Array Data File': DerivedArrayDataFileHeader,
        'Derived Array Data Matrix File': DerivedArrayDataMatrixFileHeader,
        'Derived Data File': DerivedDataFileHeader,
        'Derived Spectral Data File': DerivedSpectralDataFileHeader,
        'Raw Data File': RawDataFileHeader,
        'Raw Spectral Data File': RawSpectralDataFileHeader,
        # Process names
        'Assay Name': AssayNameHeader,
        'Data Normalization Name': DataNormalizationNameHeader,
        'Data Transformation Name': DataTransformationNameHeader,
        'Gel Electrophoresis Assay Name': GelElectrophoresisAssayNameHeader,
        'Hybridization Assay Name': HybridizationAssayNameHeader,
        'MS Assay Name': MsAssayNameHeader,
        'Normalization Name': NormalizationNameHeader,
        'Protocol REF': ProtocolRefHeader,
        # Simple headers
        'Array Design File': ArrayDesignFileHeader,
        'Array Design REF': ArrayDesignRefHeader,
        'Date': DateHeader,
        'First Dimension': FirstDimensionHeader,
        'Material Type': MaterialTypeHeader,
        'Label': LabelHeader,
        'Peptide Assignment File': PeptideAssignmentFileHeader,
        'Performer': PerformerHeader,
        'Post Translational Modification Assignment File':
            PostTranslationalModificationAssignmentFileHeader,
        'Protein Assignment File': ProteinAssignmentFileHeader,
        'Scan Name': ScanNameHeader,
        'Second Dimension': SecondDimensionHeader,
        'Spot Picking File': SpotPickingFileHeader,
        # Secondary annotations
        'Unit': UnitHeader,
        'Performer': PerformerHeader,
        'Date': DateHeader,
    }

    #: Labeled headers
    labeled_headers = {
        'Comment': CommentHeader,
        'Characteristics': CharacteristicsHeader,
        'Factor Value': FactorValueHeader,
        'Parameter Value': ParameterValueHeader,
    }

    def __init__(self, tokens, factor_refs):
        self.tokens = tokens
        self.factor_refs = factor_refs
        self.it = iter(tokens)
        self.col_no = 0

    def run(self) -> Iterator[ColumnHeader]:
        while True:
            try:
                yield self._parse_next()
            except StopIteration:
                break

    def _parse_next(self):
        # Get next value from header
        val = next(self.it)  # StopIteration is OK here
        # Process either by exact match to "Term Source REF", or other exact
        # mathes, or any of the prefix matches (e.g., "Comment[Label])"
        if val == 'Term Source REF':
            if val not in self.allowed_headers:
                tpl = 'Header "{}" not allowed in {}.'
                msg = tpl.format(val, self.file_type)
                raise ParseIsatabException(msg)
            return self._parse_term_source_ref(val)
        elif val in self.simple_headers:
            if val not in self.allowed_headers:
                tpl = 'Header "{}" not allowed in {}.'
                msg = tpl.format(val, self.file_type)
                raise ParseIsatabException(msg)
            return self._parse_simple_column_header(
                val, self.simple_headers[val])
        else:
            for label, type_ in self.labeled_headers.items():
                if val.startswith(label):
                    if label not in self.allowed_headers:
                        tpl = 'Header "{}" not allowed in {}.'
                        msg = tpl.format(label, self.file_type)
                        raise ParseIsatabException(msg)
                    return self._parse_labeled_column_header(
                        val, label, type_)
        # None of the if-statements above was taken
        tpl = 'Header "{}" unknown, processing unclear'
        msg = tpl.format(val)
        raise ParseIsatabException(msg)

    def _parse_term_source_ref(self, val):
        # Getting a StopIeration here is NOT okay, there must be a column
        # after "Term Source REF" giving the ontology the term is from.
        try:
            next(self.it)
        except StopIteration as e:
            msg = 'Expected two more columns on seeing "Term Source REF"'
            raise ParseIsatabException(msg) from e
        self.col_no += 2
        return TermRefAnnotationHeader(self.col_no - 2)

    def _parse_simple_column_header(self, val, type_):
        self.col_no += 1
        return type_(self.col_no - 1)

    def _parse_labeled_column_header(self, val, key, type_):
        tok = val[len(key):]  # strip '^{key}'
        if not tok or tok[0] != '[' or tok[-1] != ']':
            tpl = 'Problem parsing labeled header {}'
            msg = tpl.format(tpl.format(val))
            raise ParseIsatabException(msg)
        if key == 'Factor Value' and tok[1:-1] not in self.factor_refs:
            tpl = 'Factor "{}" not declared in investigation file'
            msg = tpl.format(tok[1:-1])
            raise ParseIsatabException(msg)
        self.col_no += 1
        return type_(self.col_no - 1, tok[1:-1])


class StudyHeaderParser(HeaderParserBase):
    """Helper class for parsing header of a study or assay."""

    file_type = 'study'  # for exceptions only

    allowed_headers = (
        # Material names
        'Sample Name', 'Source Name',
        # Process names
        'Protocol REF',
        # Simple headers
        'Date', 'Performer',
        # Labeled headers
        'Characteristics', 'Comment', 'Parameter Value', 'Factor Value',
        # Secondary annotations
        'Term Source REF', 'Unit')


class AssayHeaderParser(HeaderParserBase):
    """Helper class for parsing header of a assay file."""

    file_type = 'assay'  # for exceptions only

    allowed_headers = (
        # Material names
        'Extract Name', 'Labeled Extract Name', 'Material Name', 'Sample Name',
        # Data names
        'Array Data File', 'Array Data Matrix File', 'Derived Array Data File',
        'Derived Data File', 'Derived Spectral Data File',
        'Peptide Assignment File',
        'Post Translational Modification Assignment File',
        'Protein Assignment File', 'Raw Data File', 'Raw Spectral Data File',
        # Process names
        'Assay Name', 'Data Normalization Name', 'Data Transformation Name',
        'Gel Electrophoresis Assay Name', 'Hybridization Assay Name',
        'MS Assay Name', 'Normalization Name', 'Protocol REF', 'Scan Name',
        # Simple headers
        'Array Design File', 'Array Design REF', 'Date', 'First Dimension',
        'Material Type', 'Label', 'Performer', 'Scan Name', 'Second Dimension',
        'Spot Picking File',
        # Labeled headers
        'Characteristics', 'Comment', 'Parameter Value',
        # Secondary annotations
        'Term Source REF', 'Unit')

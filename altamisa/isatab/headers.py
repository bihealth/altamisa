# -*- coding: utf-8 -*-
"""This module contains code for the representation of headers from study and
assay files and parsing thereof.
"""

from __future__ import generator_stop
from typing import Iterator

from ..constants.table_headers import *  # noqa: F403
from ..exceptions import ParseIsatabException


__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"


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
        tpl = "ColumnHeader(column_type={}, col_no={}, span={})"
        return tpl.format(*map(repr, (self.column_type, self.col_no, self.span)))

    def __repr__(self):
        return str(self)


class SimpleColumnHeader(ColumnHeader):
    """Base class for simple column headers."""

    #: The value to use for the ``type`` argument.
    column_type = None

    def __init__(self, col_no):
        super().__init__(self.column_type, col_no, 1)


# Material header


class ExtractHeader(SimpleColumnHeader):
    """Extract header in an assay"""

    column_type = EXTRACT_NAME


class LabeledExtractHeader(SimpleColumnHeader):
    """Labeled Extract header in an assay"""

    column_type = LABELED_EXTRACT_NAME


class SampleHeader(SimpleColumnHeader):
    """Sample header in a study or assay"""

    column_type = SAMPLE_NAME


class SourceHeader(SimpleColumnHeader):
    """Source header in a study"""

    column_type = SOURCE_NAME


# Data header


class ArrayDataFileHeader(SimpleColumnHeader):
    """ArrayData header in an assay"""

    column_type = ARRAY_DATA_FILE


class ArrayDataMatrixFileHeader(SimpleColumnHeader):
    """ArrayData Matrix File header in an assay"""

    column_type = ARRAY_DATA_MATRIX_FILE


class ArrayDesignFileHeader(SimpleColumnHeader):
    """ArrayDesignFile header in an assay"""

    column_type = ARRAY_DESIGN_FILE


class DerivedArrayDataFileHeader(SimpleColumnHeader):
    """DerivedArrayData header in an assay"""

    column_type = DERIVED_ARRAY_DATA_FILE


class DerivedArrayDataMatrixFileHeader(SimpleColumnHeader):
    """DerivedArrayData header in an assay"""

    column_type = DERIVED_ARRAY_DATA_MATRIX_FILE


class DerivedDataFileHeader(SimpleColumnHeader):
    """Derived Data File header in an assay"""

    column_type = DERIVED_DATA_FILE


class DerivedSpectralDataFileHeader(SimpleColumnHeader):
    """DerivedSpectralData header in an assay"""

    column_type = DERIVED_SPECTRAL_DATA_FILE


class ImageFileHeader(SimpleColumnHeader):
    """Image File header in an assay"""

    column_type = IMAGE_FILE


class MetaboliteAssignmentFileHeader(SimpleColumnHeader):
    """PeptideAssignment header in an assay"""

    column_type = METABOLITE_ASSIGNMENT_FILE


class PeptideAssignmentFileHeader(SimpleColumnHeader):
    """PeptideAssignment header in an assay"""

    column_type = PEPTIDE_ASSIGNMENT_FILE


class PostTranslationalModificationAssignmentFileHeader(SimpleColumnHeader):
    """PostTranslationalModificationAssignment header in an assay"""

    column_type = POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE


class ProteinAssignmentFileHeader(SimpleColumnHeader):
    """ProteinAssignment header in an assay"""

    column_type = PROTEIN_ASSIGNMENT_FILE


class RawDataFileHeader(SimpleColumnHeader):
    """Raw Data header in an assay"""

    column_type = RAW_DATA_FILE


class RawSpectralDataFileHeader(SimpleColumnHeader):
    """Raw Spectral Data header in an assay"""

    column_type = RAW_SPECTRAL_DATA_FILE


class SpotPickingFileHeader(SimpleColumnHeader):
    """SpotPickingFile header in an assay"""

    column_type = SPOT_PICKING_FILE


# Assay header


class AssayNameHeader(SimpleColumnHeader):
    """Assay Name header in an assay"""

    column_type = ASSAY_NAME


class DataTransformationNameHeader(SimpleColumnHeader):
    """DataTransformationName header in an assay"""

    column_type = DATA_TRANSFORMATION_NAME


class GelElectrophoresisAssayNameHeader(SimpleColumnHeader):
    """GelElectrophoresisAssayName header in an assay"""

    column_type = GEL_ELECTROPHORESIS_ASSAY_NAME


class HybridizationAssayNameHeader(SimpleColumnHeader):
    """HybridizationAssayName header in an assay"""

    column_type = HYBRIDIZATION_ASSAY_NAME


class MsAssayNameHeader(SimpleColumnHeader):
    """MsAssayName header in an assay"""

    column_type = MS_ASSAY_NAME


class NormalizationNameHeader(SimpleColumnHeader):
    """Normalization Name header in a assay"""

    column_type = NORMALIZATION_NAME


class ProtocolRefHeader(SimpleColumnHeader):
    """Protocol REF header in a study or assay"""

    column_type = PROTOCOL_REF


class ScanNameHeader(SimpleColumnHeader):
    """ScanName header in assay"""

    column_type = SCAN_NAME


# Other simple header


class ArrayDesignRefHeader(SimpleColumnHeader):
    """ArrayDesignRef header in an assay"""

    column_type = ARRAY_DESIGN_REF


class DateHeader(SimpleColumnHeader):
    """Date annotation header in a study or assay"""

    column_type = DATE


class FirstDimensionHeader(SimpleColumnHeader):
    """First Dimension header in an assay"""

    column_type = FIRST_DIMENSION


class LabelHeader(SimpleColumnHeader):
    """Material Type header in an assay"""

    column_type = LABEL


class MaterialTypeHeader(SimpleColumnHeader):
    """Material Type header in an assay"""

    column_type = MATERIAL_TYPE


class PerformerHeader(SimpleColumnHeader):
    """Performer header in an assay"""

    column_type = PERFORMER


class SecondDimensionHeader(SimpleColumnHeader):
    """SecondDimension header in an assay"""

    column_type = SECOND_DIMENSION


class TermRefAnnotationHeader(ColumnHeader):
    """Term reference annotation header"""

    def __init__(self, col_no):
        super().__init__(TERM_SOURCE_REF, col_no, 2)


class UnitHeader(SimpleColumnHeader):
    """Unit annotation header in a study or assay"""

    column_type = UNIT


# Labeled header


class LabeledColumnHeader(ColumnHeader):
    """Base class for labeled column headers."""

    #: The value to use for the ``type`` argument.
    column_type = None

    def __init__(self, col_no, label):
        super().__init__(self.column_type, col_no, 1)
        self.label = label

    def __str__(self):
        tpl = "LabeledColumnHeader(" "column_type={}, col_no={}, span={}, label={})"
        return tpl.format(*map(repr, (self.column_type, self.col_no, self.span, self.label)))


class CharacteristicsHeader(LabeledColumnHeader):
    """Protocol Characteristics[*] header in a study or assay"""

    column_type = CHARACTERISTICS


class CommentHeader(LabeledColumnHeader):
    """Comment header in a study or assay"""

    column_type = COMMENT


class FactorValueHeader(LabeledColumnHeader):
    """Protocol ``Factor Value[*]`` header in a study or assay"""

    column_type = FACTOR_VALUE


class ParameterValueHeader(LabeledColumnHeader):
    """Protocol ``Parameter Value[*]`` header in a study or assay"""

    column_type = PARAMETER_VALUE


# Header parsers


class HeaderParserBase:
    """Helper base class for parsing a header from a study or assay file."""

    #: Names of the allowed headers
    allowed_headers = None

    #: Headers that are mapped to ``SimpleColumnHeader``s
    simple_headers = {
        # Material headers
        EXTRACT_NAME: ExtractHeader,
        LABELED_EXTRACT_NAME: LabeledExtractHeader,
        SAMPLE_NAME: SampleHeader,
        SOURCE_NAME: SourceHeader,
        # Data headers
        ARRAY_DATA_FILE: ArrayDataFileHeader,
        ARRAY_DATA_MATRIX_FILE: ArrayDataMatrixFileHeader,
        ARRAY_DESIGN_FILE: ArrayDesignFileHeader,
        DERIVED_ARRAY_DATA_FILE: DerivedArrayDataFileHeader,
        DERIVED_ARRAY_DATA_MATRIX_FILE: DerivedArrayDataMatrixFileHeader,
        DERIVED_DATA_FILE: DerivedDataFileHeader,
        DERIVED_SPECTRAL_DATA_FILE: DerivedSpectralDataFileHeader,
        IMAGE_FILE: ImageFileHeader,
        METABOLITE_ASSIGNMENT_FILE: MetaboliteAssignmentFileHeader,
        PEPTIDE_ASSIGNMENT_FILE: PeptideAssignmentFileHeader,
        POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE: PostTranslationalModificationAssignmentFileHeader,
        PROTEIN_ASSIGNMENT_FILE: ProteinAssignmentFileHeader,
        RAW_DATA_FILE: RawDataFileHeader,
        RAW_SPECTRAL_DATA_FILE: RawSpectralDataFileHeader,
        SPOT_PICKING_FILE: SpotPickingFileHeader,
        # Process names or Ref
        ASSAY_NAME: AssayNameHeader,
        DATA_TRANSFORMATION_NAME: DataTransformationNameHeader,
        GEL_ELECTROPHORESIS_ASSAY_NAME: GelElectrophoresisAssayNameHeader,
        HYBRIDIZATION_ASSAY_NAME: HybridizationAssayNameHeader,
        MS_ASSAY_NAME: MsAssayNameHeader,
        NORMALIZATION_NAME: NormalizationNameHeader,
        PROTOCOL_REF: ProtocolRefHeader,
        SCAN_NAME: ScanNameHeader,
        # Simple headers
        ARRAY_DESIGN_REF: ArrayDesignRefHeader,
        DATE: DateHeader,
        FIRST_DIMENSION: FirstDimensionHeader,
        LABEL: LabelHeader,
        MATERIAL_TYPE: MaterialTypeHeader,
        PERFORMER: PerformerHeader,
        SECOND_DIMENSION: SecondDimensionHeader,
        # Secondary annotations
        UNIT: UnitHeader,
    }

    #: Labeled headers
    labeled_headers = {
        CHARACTERISTICS: CharacteristicsHeader,
        COMMENT: CommentHeader,
        FACTOR_VALUE: FactorValueHeader,
        PARAMETER_VALUE: ParameterValueHeader,
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
        # matches, or any of the prefix matches (e.g., "Comment[Label])"
        if val == TERM_SOURCE_REF:
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
            return self._parse_simple_column_header(val, self.simple_headers[val])
        else:
            for label, type_ in self.labeled_headers.items():
                if val.startswith(label):
                    if label not in self.allowed_headers:
                        tpl = 'Header "{}" not allowed in {}.'
                        msg = tpl.format(label, self.file_type)
                        raise ParseIsatabException(msg)
                    return self._parse_labeled_column_header(val, label, type_)
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
        tok = val[len(key) :]  # strip '^{key}'
        if not tok or tok[0] != "[" or tok[-1] != "]":
            tpl = "Problem parsing labeled header {}"
            msg = tpl.format(tpl.format(val))
            raise ParseIsatabException(msg)
        if key == "Factor Value" and tok[1:-1] not in self.factor_refs:
            tpl = 'Factor "{}" not declared in investigation file'
            msg = tpl.format(tok[1:-1])
            raise ParseIsatabException(msg)
        self.col_no += 1
        return type_(self.col_no - 1, tok[1:-1])


class StudyHeaderParser(HeaderParserBase):
    """Helper class for parsing header of a study or assay."""

    file_type = "study"  # for exceptions only

    allowed_headers = (
        # Material names
        SAMPLE_NAME,
        SOURCE_NAME,
        # Process names
        PROTOCOL_REF,
        # Simple headers
        DATE,
        PERFORMER,
        # Labeled headers
        CHARACTERISTICS,
        COMMENT,
        FACTOR_VALUE,
        PARAMETER_VALUE,
        # Secondary annotations
        TERM_SOURCE_REF,
        UNIT,
    )


class AssayHeaderParser(HeaderParserBase):
    """Helper class for parsing header of a assay file."""

    file_type = "assay"  # for exceptions only

    allowed_headers = (
        # Material names
        EXTRACT_NAME,
        LABELED_EXTRACT_NAME,
        SAMPLE_NAME,
        # Data names
        ARRAY_DATA_FILE,
        ARRAY_DATA_MATRIX_FILE,
        ARRAY_DESIGN_FILE,
        DERIVED_ARRAY_DATA_FILE,
        DERIVED_ARRAY_DATA_MATRIX_FILE,
        DERIVED_DATA_FILE,
        DERIVED_SPECTRAL_DATA_FILE,
        IMAGE_FILE,
        METABOLITE_ASSIGNMENT_FILE,
        PEPTIDE_ASSIGNMENT_FILE,
        POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE,
        PROTEIN_ASSIGNMENT_FILE,
        RAW_DATA_FILE,
        RAW_SPECTRAL_DATA_FILE,
        SPOT_PICKING_FILE,
        # Process names or Ref
        ASSAY_NAME,
        DATA_TRANSFORMATION_NAME,
        GEL_ELECTROPHORESIS_ASSAY_NAME,
        HYBRIDIZATION_ASSAY_NAME,
        MS_ASSAY_NAME,
        NORMALIZATION_NAME,
        PROTOCOL_REF,
        SCAN_NAME,
        # Simple headers
        ARRAY_DESIGN_REF,
        DATE,
        FIRST_DIMENSION,
        LABEL,
        MATERIAL_TYPE,
        PERFORMER,
        SECOND_DIMENSION,
        # Labeled headers
        CHARACTERISTICS,
        COMMENT,
        PARAMETER_VALUE,
        # Secondary annotations
        TERM_SOURCE_REF,
        UNIT,
    )

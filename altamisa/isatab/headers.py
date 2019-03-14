# -*- coding: utf-8 -*-
"""This module contains code for the representation of headers from study and
assay files and parsing thereof.
"""

from __future__ import generator_stop
from typing import Iterator, List

from ..constants import table_headers
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

    def get_simple_string(self) -> List[str]:
        """Return a list of simple string representations of the column types"""
        return [self.column_type]


class SimpleColumnHeader(ColumnHeader):
    """Base class for simple column headers."""

    #: The value to use for the ``type`` argument.
    column_type = None

    def __init__(self, col_no):
        super().__init__(self.column_type, col_no, 1)


# Material header


class ExtractHeader(SimpleColumnHeader):
    """Extract header in an assay"""

    column_type = table_headers.EXTRACT_NAME


class LabeledExtractHeader(SimpleColumnHeader):
    """Labeled Extract header in an assay"""

    column_type = table_headers.LABELED_EXTRACT_NAME


class LibraryHeader(SimpleColumnHeader):
    """Library header in an assay"""

    column_type = table_headers.LIBRARY_NAME


class SampleHeader(SimpleColumnHeader):
    """Sample header in a study or assay"""

    column_type = table_headers.SAMPLE_NAME


class SourceHeader(SimpleColumnHeader):
    """Source header in a study"""

    column_type = table_headers.SOURCE_NAME


# Data header


class ArrayDataFileHeader(SimpleColumnHeader):
    """ArrayData header in an assay"""

    column_type = table_headers.ARRAY_DATA_FILE


class ArrayDataMatrixFileHeader(SimpleColumnHeader):
    """ArrayData Matrix File header in an assay"""

    column_type = table_headers.ARRAY_DATA_MATRIX_FILE


class ArrayDesignFileHeader(SimpleColumnHeader):
    """ArrayDesignFile header in an assay"""

    column_type = table_headers.ARRAY_DESIGN_FILE


class DerivedArrayDataFileHeader(SimpleColumnHeader):
    """DerivedArrayData header in an assay"""

    column_type = table_headers.DERIVED_ARRAY_DATA_FILE


class DerivedArrayDataMatrixFileHeader(SimpleColumnHeader):
    """DerivedArrayData header in an assay"""

    column_type = table_headers.DERIVED_ARRAY_DATA_MATRIX_FILE


class DerivedDataFileHeader(SimpleColumnHeader):
    """Derived Data File header in an assay"""

    column_type = table_headers.DERIVED_DATA_FILE


class DerivedSpectralDataFileHeader(SimpleColumnHeader):
    """DerivedSpectralData header in an assay"""

    column_type = table_headers.DERIVED_SPECTRAL_DATA_FILE


class ImageFileHeader(SimpleColumnHeader):
    """Image File header in an assay"""

    column_type = table_headers.IMAGE_FILE


class MetaboliteAssignmentFileHeader(SimpleColumnHeader):
    """PeptideAssignment header in an assay"""

    column_type = table_headers.METABOLITE_ASSIGNMENT_FILE


class PeptideAssignmentFileHeader(SimpleColumnHeader):
    """PeptideAssignment header in an assay"""

    column_type = table_headers.PEPTIDE_ASSIGNMENT_FILE


class PostTranslationalModificationAssignmentFileHeader(SimpleColumnHeader):
    """PostTranslationalModificationAssignment header in an assay"""

    column_type = table_headers.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE


class ProteinAssignmentFileHeader(SimpleColumnHeader):
    """ProteinAssignment header in an assay"""

    column_type = table_headers.PROTEIN_ASSIGNMENT_FILE


class RawDataFileHeader(SimpleColumnHeader):
    """Raw Data header in an assay"""

    column_type = table_headers.RAW_DATA_FILE


class RawSpectralDataFileHeader(SimpleColumnHeader):
    """Raw Spectral Data header in an assay"""

    column_type = table_headers.RAW_SPECTRAL_DATA_FILE


class SpotPickingFileHeader(SimpleColumnHeader):
    """SpotPickingFile header in an assay"""

    column_type = table_headers.SPOT_PICKING_FILE


# Assay header


class AssayNameHeader(SimpleColumnHeader):
    """Assay Name header in an assay"""

    column_type = table_headers.ASSAY_NAME


class DataTransformationNameHeader(SimpleColumnHeader):
    """DataTransformationName header in an assay"""

    column_type = table_headers.DATA_TRANSFORMATION_NAME


class GelElectrophoresisAssayNameHeader(SimpleColumnHeader):
    """GelElectrophoresisAssayName header in an assay"""

    column_type = table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME


class HybridizationAssayNameHeader(SimpleColumnHeader):
    """HybridizationAssayName header in an assay"""

    column_type = table_headers.HYBRIDIZATION_ASSAY_NAME


class MsAssayNameHeader(SimpleColumnHeader):
    """MsAssayName header in an assay"""

    column_type = table_headers.MS_ASSAY_NAME


class NormalizationNameHeader(SimpleColumnHeader):
    """Normalization Name header in a assay"""

    column_type = table_headers.NORMALIZATION_NAME


class ProtocolRefHeader(SimpleColumnHeader):
    """Protocol REF header in a study or assay"""

    column_type = table_headers.PROTOCOL_REF


class ScanNameHeader(SimpleColumnHeader):
    """ScanName header in assay"""

    column_type = table_headers.SCAN_NAME


# Other simple header


class ArrayDesignRefHeader(SimpleColumnHeader):
    """ArrayDesignRef header in an assay"""

    column_type = table_headers.ARRAY_DESIGN_REF


class DateHeader(SimpleColumnHeader):
    """Date annotation header in a study or assay"""

    column_type = table_headers.DATE


class FirstDimensionHeader(SimpleColumnHeader):
    """First Dimension header in an assay"""

    column_type = table_headers.FIRST_DIMENSION


class LabelHeader(SimpleColumnHeader):
    """Label header in an assay"""

    column_type = table_headers.LABEL


class MaterialTypeHeader(SimpleColumnHeader):
    """Material Type header in an assay"""

    column_type = table_headers.MATERIAL_TYPE


class PerformerHeader(SimpleColumnHeader):
    """Performer header in an assay"""

    column_type = table_headers.PERFORMER


class SecondDimensionHeader(SimpleColumnHeader):
    """Second Dimension header in an assay"""

    column_type = table_headers.SECOND_DIMENSION


class TermRefAnnotationHeader(ColumnHeader):
    """Term reference annotation header"""

    def __init__(self, col_no):
        super().__init__(table_headers.TERM_SOURCE_REF, col_no, 2)

    def get_simple_string(self) -> List[str]:
        """Return a list of simple string representations of the column types"""
        return [table_headers.TERM_SOURCE_REF, table_headers.TERM_ACCESSION_NUMBER]


class UnitHeader(SimpleColumnHeader):
    """Unit annotation header in a study or assay"""

    column_type = table_headers.UNIT


# Labeled header


class LabeledColumnHeader(ColumnHeader):
    """Base class for labeled column headers."""

    #: The value to use for the ``type`` argument.
    column_type = None

    def __init__(self, col_no, label):
        super().__init__(self.column_type, col_no, 1)
        self.label = label

    def __str__(self):
        tpl = "LabeledColumnHeader(column_type={}, col_no={}, span={}, label={})"
        return tpl.format(*map(repr, (self.column_type, self.col_no, self.span, self.label)))

    def __repr__(self):
        return str(self)

    def get_simple_string(self):
        """Return a list of simple string representations of the column types"""
        return ["".join((self.column_type, "[", self.label, "]"))]


class CharacteristicsHeader(LabeledColumnHeader):
    """Material ``Characteristics[*]`` header in a study or assay"""

    column_type = table_headers.CHARACTERISTICS


class CommentHeader(LabeledColumnHeader):
    """``Comment`` header in a study or assay"""

    column_type = table_headers.COMMENT


class FactorValueHeader(LabeledColumnHeader):
    """``Factor Value[*]`` header in a study or assay"""

    column_type = table_headers.FACTOR_VALUE


class ParameterValueHeader(LabeledColumnHeader):
    """Protocol ``Parameter Value[*]`` header in a study or assay"""

    column_type = table_headers.PARAMETER_VALUE


# Header parsers


class HeaderParserBase:
    """
    Helper base class for parsing a header from a study or assay file.

    :type tokens: list
    :param tokens: List of strings, e.g. a split line read from a tsv/cvs file.
    """

    #: Names of the allowed headers
    allowed_headers = None

    #: Headers that are mapped to ``SimpleColumnHeader``
    simple_headers = {
        # Material headers
        table_headers.EXTRACT_NAME: ExtractHeader,
        table_headers.LABELED_EXTRACT_NAME: LabeledExtractHeader,
        table_headers.LIBRARY_NAME: LibraryHeader,
        table_headers.SAMPLE_NAME: SampleHeader,
        table_headers.SOURCE_NAME: SourceHeader,
        # Data headers
        table_headers.ARRAY_DATA_FILE: ArrayDataFileHeader,
        table_headers.ARRAY_DATA_MATRIX_FILE: ArrayDataMatrixFileHeader,
        table_headers.ARRAY_DESIGN_FILE: ArrayDesignFileHeader,
        table_headers.DERIVED_ARRAY_DATA_FILE: DerivedArrayDataFileHeader,
        table_headers.DERIVED_ARRAY_DATA_MATRIX_FILE: DerivedArrayDataMatrixFileHeader,
        table_headers.DERIVED_DATA_FILE: DerivedDataFileHeader,
        table_headers.DERIVED_SPECTRAL_DATA_FILE: DerivedSpectralDataFileHeader,
        table_headers.IMAGE_FILE: ImageFileHeader,
        table_headers.METABOLITE_ASSIGNMENT_FILE: MetaboliteAssignmentFileHeader,
        table_headers.PEPTIDE_ASSIGNMENT_FILE: PeptideAssignmentFileHeader,
        table_headers.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE: PostTranslationalModificationAssignmentFileHeader,
        table_headers.PROTEIN_ASSIGNMENT_FILE: ProteinAssignmentFileHeader,
        table_headers.RAW_DATA_FILE: RawDataFileHeader,
        table_headers.RAW_SPECTRAL_DATA_FILE: RawSpectralDataFileHeader,
        table_headers.SPOT_PICKING_FILE: SpotPickingFileHeader,
        # Process names or Ref
        table_headers.ASSAY_NAME: AssayNameHeader,
        table_headers.DATA_TRANSFORMATION_NAME: DataTransformationNameHeader,
        table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME: GelElectrophoresisAssayNameHeader,
        table_headers.HYBRIDIZATION_ASSAY_NAME: HybridizationAssayNameHeader,
        table_headers.MS_ASSAY_NAME: MsAssayNameHeader,
        table_headers.NORMALIZATION_NAME: NormalizationNameHeader,
        table_headers.PROTOCOL_REF: ProtocolRefHeader,
        table_headers.SCAN_NAME: ScanNameHeader,
        # Simple headers
        table_headers.ARRAY_DESIGN_REF: ArrayDesignRefHeader,
        table_headers.DATE: DateHeader,
        table_headers.FIRST_DIMENSION: FirstDimensionHeader,
        table_headers.LABEL: LabelHeader,
        table_headers.MATERIAL_TYPE: MaterialTypeHeader,
        table_headers.PERFORMER: PerformerHeader,
        table_headers.SECOND_DIMENSION: SecondDimensionHeader,
        # Secondary annotations
        table_headers.UNIT: UnitHeader,
    }

    #: Labeled headers
    labeled_headers = {
        table_headers.CHARACTERISTICS: CharacteristicsHeader,
        table_headers.COMMENT: CommentHeader,
        table_headers.FACTOR_VALUE: FactorValueHeader,
        table_headers.PARAMETER_VALUE: ParameterValueHeader,
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.it = iter(tokens)
        self.col_no = 0

    def run(self) -> Iterator[ColumnHeader]:
        """Parse the header"""
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
        if val == table_headers.TERM_SOURCE_REF:
            return self._parse_term_source_ref()
        elif val in self.simple_headers:
            if val not in self.allowed_headers:
                tpl = 'Header "{}" not allowed in {}.'
                msg = tpl.format(val, self.file_type)
                raise ParseIsatabException(msg)
            return self._parse_simple_column_header(self.simple_headers[val])
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

    def _parse_term_source_ref(self):
        # Getting a StopIteration here is NOT okay, there must be a column
        # after "Term Source REF" giving the ontology the term is from.
        try:
            val = next(self.it)
        except StopIteration as e:
            msg = 'Expected one more column on seeing "Term Source REF"'
            raise ParseIsatabException(msg) from e
        if val != table_headers.TERM_ACCESSION_NUMBER:
            msg = 'Expected column "Term Accession Number" after seeing "Term Source REF"'
            raise ParseIsatabException(msg)
        self.col_no += 2
        return TermRefAnnotationHeader(self.col_no - 2)

    def _parse_simple_column_header(self, type_):
        self.col_no += 1
        return type_(self.col_no - 1)

    def _parse_labeled_column_header(self, val, key, type_):
        tok = val[len(key) :]  # strip '^{key}'
        if not tok or tok[0] != "[" or tok[-1] != "]":
            tpl = "Problem parsing labeled header {}"
            msg = tpl.format(val)
            raise ParseIsatabException(msg)
        self.col_no += 1
        return type_(self.col_no - 1, tok[1:-1])


class StudyHeaderParser(HeaderParserBase):
    """Helper class for parsing header of a study or assay."""

    file_type = "study"  # for exceptions only

    allowed_headers = (
        # Material names
        table_headers.SAMPLE_NAME,
        table_headers.SOURCE_NAME,
        # Process names
        table_headers.PROTOCOL_REF,
        # Simple headers
        table_headers.DATE,
        table_headers.PERFORMER,
        # Labeled headers
        table_headers.CHARACTERISTICS,
        table_headers.COMMENT,
        table_headers.FACTOR_VALUE,
        table_headers.PARAMETER_VALUE,
        # Secondary annotations
        table_headers.TERM_SOURCE_REF,
        table_headers.UNIT,
    )


class AssayHeaderParser(HeaderParserBase):
    """Helper class for parsing header of a assay file."""

    file_type = "assay"  # for exceptions only

    allowed_headers = (
        # Material names
        table_headers.EXTRACT_NAME,
        table_headers.LABELED_EXTRACT_NAME,
        table_headers.LIBRARY_NAME,
        table_headers.SAMPLE_NAME,
        # Data names
        table_headers.ARRAY_DATA_FILE,
        table_headers.ARRAY_DATA_MATRIX_FILE,
        table_headers.ARRAY_DESIGN_FILE,
        table_headers.DERIVED_ARRAY_DATA_FILE,
        table_headers.DERIVED_ARRAY_DATA_MATRIX_FILE,
        table_headers.DERIVED_DATA_FILE,
        table_headers.DERIVED_SPECTRAL_DATA_FILE,
        table_headers.IMAGE_FILE,
        table_headers.METABOLITE_ASSIGNMENT_FILE,
        table_headers.PEPTIDE_ASSIGNMENT_FILE,
        table_headers.POST_TRANSLATIONAL_MODIFICATION_ASSIGNMENT_FILE,
        table_headers.PROTEIN_ASSIGNMENT_FILE,
        table_headers.RAW_DATA_FILE,
        table_headers.RAW_SPECTRAL_DATA_FILE,
        table_headers.SPOT_PICKING_FILE,
        # Process names or Ref
        table_headers.ASSAY_NAME,
        table_headers.DATA_TRANSFORMATION_NAME,
        table_headers.GEL_ELECTROPHORESIS_ASSAY_NAME,
        table_headers.HYBRIDIZATION_ASSAY_NAME,
        table_headers.MS_ASSAY_NAME,
        table_headers.NORMALIZATION_NAME,
        table_headers.PROTOCOL_REF,
        table_headers.SCAN_NAME,
        # Simple headers
        table_headers.ARRAY_DESIGN_REF,
        table_headers.DATE,
        table_headers.FIRST_DIMENSION,
        table_headers.LABEL,
        table_headers.MATERIAL_TYPE,
        table_headers.PERFORMER,
        table_headers.SECOND_DIMENSION,
        # Labeled headers
        table_headers.CHARACTERISTICS,
        table_headers.COMMENT,
        table_headers.PARAMETER_VALUE,
        # Secondary annotations
        table_headers.TERM_SOURCE_REF,
        table_headers.UNIT,
    )

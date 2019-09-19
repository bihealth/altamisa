# -*- coding: utf-8 -*-
"""This module contains code for the parsing of assay and study files.
"""


from __future__ import generator_stop
import csv
import functools
import os
from typing import NamedTuple, TextIO

from ..constants import table_headers
from ..constants.table_tokens import TOKEN_UNKNOWN
from ..exceptions import WriteIsatabException
from .headers import AssayHeaderParser, StudyHeaderParser
from .helpers import is_ontology_term_ref
from .models import Material, OntologyTermRef, Process


__author__ = (
    "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>, "
    "Mathias Kuhring <mathias.kuhring@bihealth.de>"
)


# Graph traversal -------------------------------------------------------


class _Digraph:
    """Simple class encapsulating directed graph with vertices and arcs"""

    def __init__(self, vertices, arcs, predicate_is_starting):
        #: Graph vertices/nodes (models.Material and models.Process)
        self.vertices = vertices
        #: Graph arcs/edges (models.Arc)
        self.arcs = arcs
        #: Name to node mapping
        self.v_by_name = {v.unique_name: v for v in self.vertices}
        #: Arcs as tuple of tail and head
        self.a_by_name = {(a[0], a[1]): None for a in self.arcs}
        #: Names of starting nodes
        self.source_names = [v.unique_name for v in self.vertices if predicate_is_starting(v)]
        #: Outgoing vertices/nodes
        self.outgoing = {}

        for s_name, t_name in self.a_by_name.keys():
            self.outgoing.setdefault(s_name, []).append(t_name)


class _UnionFind:
    """Union-Find (disjoint set) data structure allowing to address by vertex
    name"""

    def __init__(self, vertex_names):
        #: Node name to id mapping
        self._name_to_id = {v: i for i, v in enumerate(vertex_names)}
        #: Pointer to the containing sets
        self._id = list(range(len(vertex_names)))
        #: Size of the set (_sz[_id[v]] is the size of the set that contains v)
        self._sz = [1] * len(vertex_names)

    def find(self, v):
        assert type(v) is int
        j = v

        while j != self._id[j]:
            self._id[j] = self._id[self._id[j]]
            j = self._id[j]

        return j

    def find_by_name(self, v_name):
        return self.find(self._name_to_id[v_name])

    def union_by_name(self, v_name, w_name):
        self.union(self.find_by_name(v_name), self.find_by_name(w_name))

    def union(self, v, w):
        assert type(v) is int
        assert type(w) is int
        i = self.find(v)
        j = self.find(w)

        if i == j:
            return

        if self._sz[i] < self._sz[j]:
            self._id[i] = j
            self._sz[j] += self._sz[i]

        else:
            self._id[j] = i

        self._sz[i] += self._sz[j]


def _is_of_starting_type(starting_type, v):
    """Predicate to select vertices based on starting type."""
    return getattr(v, "type", None) == starting_type


class RefTableBuilder:
    """Class for building reference table from a graph"""

    def __init__(self, nodes, arcs, predicate_is_starting):
        # Input directed graph
        self.digraph = _Digraph(nodes, arcs, predicate_is_starting)
        #: Output table rows
        self._rows = []

    def _partition(self):
        uf = _UnionFind(self.digraph.v_by_name.keys())

        for arc in self.digraph.arcs:
            uf.union_by_name(arc[0], arc[1])

        result = {}

        for v_name in self.digraph.v_by_name.keys():
            result.setdefault(v_name, []).append(v_name)

        return list(result.values())

    def _dump_row(self, v_names):
        self._rows.append(list(v_names))

    def _dfs(self, source, path):
        next_v_names = None

        if source in self.digraph.outgoing:
            next_v_names = self.digraph.outgoing[source]

        if next_v_names:
            for target in next_v_names:
                path.append(target)
                self._dfs(target, path)
                path.pop()

        else:
            self._dump_row(path)

    def _process_component(self, v_names):
        # NB: The algorithm below looks a bit involved but it's the simplest way without an
        # external library to get the intersection of two lists of strings in the same order as
        # in the input file and still using hashing for lookup.
        intersection = set(v_names) & set(self.digraph.source_names)
        sources_set = set()
        sources = []
        for name in self.digraph.source_names:
            if name in intersection and name not in sources_set:
                sources_set.add(name)
                sources.append(name)

        for source in sources:
            self._dfs(source, [source])

    def run(self):
        components = self._partition()

        for component in components:
            self._process_component(component)

        return self._rows


# Write classes ------------------------------------------------------------------------------------


class _WriterBase:
    """Base class that writes a file from an ``Study`` or ``Assay`` object.
    """

    #: Note type starting a graph
    _starting_type = None

    #: Parser for study or assay headers
    _header_parser = None

    @classmethod
    def from_stream(
        cls, study_or_assay: NamedTuple, output_file: TextIO, quote=None, lineterminator=None
    ):
        """Construct from file-like object"""
        return cls(study_or_assay, output_file, quote, lineterminator)

    def __init__(
        self, study_or_assay: NamedTuple, output_file: TextIO, quote=None, lineterminator=None
    ):
        # Study or Assay model
        self._model = study_or_assay
        # Nodes in the model (all materials/data and processes)
        self._nodes = {**self._model.materials, **self._model.processes}
        # Output file
        self.output_file = output_file
        # Character for quoting
        self.quote = quote
        # Csv file writer
        self._writer = csv.writer(
            output_file,
            delimiter="\t",
            lineterminator=lineterminator or os.linesep,
            quoting=csv.QUOTE_ALL if self.quote else csv.QUOTE_NONE,
            # Can't use no quoting without escaping, so use different dummy quote here
            escapechar="\\",
            quotechar=self.quote if self.quote else "|",
        )
        # Reference table for output
        self._ref_table = None
        # Headers for output
        self._headers = None

    def _write_next_line(self, line: [str]):
        """Write next line."""
        self._writer.writerow(line)

    def _extract_headers(self):
        """
        Extract reference header from first row, assuming for now all nodes in one column have
        the same header resp. same attributes (names, characteristics, comments etc.) available.
        Something the independent validation should check and maybe correct for.
        """
        self._headers = []
        for node in [self._nodes[node] for node in self._ref_table[0]]:
            # For now, assume that each node brings the list of original headers
            # and that the headers match the available attributes
            if node.headers:
                # TODO: check that headers and attributes match
                self._headers.append(list(self._header_parser(node.headers).run()))
                # self._headers.append(node.headers)
            else:  # pragma: no cover
                # TODO: create new headers based on attributes
                tpl = "No reference headers available in node {} of first row"
                msg = tpl.format(node.unique_name)
                raise WriteIsatabException(msg)

    def _write_headers(self):
        # Unlist node headers
        headers = [s for headers in self._headers for h in headers for s in h.get_simple_string()]
        self._write_next_line(headers)

    def _extract_and_write_nodes(self):
        # Extract and write all nodes in the order given by the reference table
        for row in self._ref_table:
            # Number of nodes per row must match number of header groups
            if len(row) < len(self._headers):
                tpl = (
                    "Fewer nodes in row than header groups available:"
                    "\n\tHeader groups:\t{}\n\tRow nodes:\t{}"
                )
                msg = tpl.format(self._headers, row)
                raise WriteIsatabException(msg)
            elif len(row) > len(self._headers):
                tpl = (
                    "More nodes in row than header groups available:"
                    "\n\tHeader groups:\t{}\n\tRow nodes:\t{}"
                )
                msg = tpl.format(self._headers, row)
                raise WriteIsatabException(msg)

            # Iterate nodes and corresponding headers
            line = []
            for node_name, headers in zip(row, self._headers):
                # Extract node attributes
                node = self._nodes[node_name]
                attributes = self._extract_attributes(node)
                self._previous_attribute = None
                for header in headers:
                    header = header.get_simple_string()[0]
                    # Append next attribute according to header
                    self._append_attribute(line, attributes, header, node)
                # Iterating the headers should deplete attributes
                if len(attributes) > 0:  # pragma: no cover
                    tpl = "Leftover attributes {} found in node {}"
                    msg = tpl.format(attributes, node.unique_name)
                    raise WriteIsatabException(msg)
            self._write_next_line(line)

    def _append_attribute(self, line, attributes, header, node):
        # Append the next attribute according to header
        if header in attributes:
            attribute = attributes.pop(header)
            # Append expected ontology reference
            if header == table_headers.TERM_SOURCE_REF:
                self._append_attribute_ontology_reference(line, attribute, header, node)
            # Append attribute with value
            # (Characteristics, Comment, FactorValue, ParameterValue)
            elif hasattr(attribute, "value"):
                self._append_attribute_with_value(line, attribute, attributes)
            # Append attribute with direct ontology:
            # (extract_label, first_dimension, material_type, second_dimension)
            elif is_ontology_term_ref(attribute):
                line.append(attribute.name)
                attributes[table_headers.TERM_SOURCE_REF] = attribute
            # Append attributes with string only (everything else)
            else:
                line.append(attribute)
            self._previous_attribute = attribute
        else:  # pragma: no cover
            tpl = "Expected '{}' not found in node '{}' after/for attribute '{}'"
            msg = tpl.format(header, node.unique_name, self._previous_attribute)
            raise WriteIsatabException(msg)

    @staticmethod
    def _append_attribute_ontology_reference(line, attribute, header, node):
        # Append expected ontology reference
        if is_ontology_term_ref(attribute):
            line.extend([attribute.ontology_name or "", attribute.accession or ""])
        else:  # pragma: no cover
            tpl = "Expected {} not found in attribute {} of node {}"
            msg = tpl.format(header, attribute, node.unique_name)
            raise WriteIsatabException(msg)

    @staticmethod
    def _append_attribute_with_value(line, attribute, attributes):
        # Append attribute with a value and potentially a unit
        # (Characteristics, Comment, FactorValue, ParameterValue)

        # If available, add Ontology to dict for next header
        if is_ontology_term_ref(attribute.value):
            line.append(attribute.value.name or "")
            attributes[table_headers.TERM_SOURCE_REF] = attribute.value
        # Cases for attributes with lists of values allowed (Characteristics, ParameterValue)
        elif isinstance(attribute.value, list):
            if is_ontology_term_ref(attribute.value[0]):
                name = ";".join(
                    [v.name.replace(";", "\\;") if v.name else "" for v in attribute.value]
                )
                accession = ";".join(
                    [
                        v.accession.replace(";", "\\;") if v.accession else ""
                        for v in attribute.value
                    ]
                )
                ontology_name = ";".join(
                    [
                        v.ontology_name.replace(";", "\\;") if v.ontology_name else ""
                        for v in attribute.value
                    ]
                )
                tmp_term_ref = OntologyTermRef(name, accession, ontology_name)
                line.append(name or "")
                attributes[table_headers.TERM_SOURCE_REF] = tmp_term_ref
            else:
                line.append(";".join([v.replace(";", "\\;") if v else "" for v in attribute.value]))
        else:
            line.append(attribute.value)
        # If available, add Unit to dict for next header
        # (Characteristics, FactorValue, ParameterValue)
        if hasattr(attribute, "unit") and attribute.unit is not None:
            if is_ontology_term_ref(attribute.unit):
                attributes[table_headers.UNIT] = attribute.unit.name
                attributes[table_headers.TERM_SOURCE_REF] = attribute.unit
            else:
                attributes[table_headers.UNIT] = attribute.unit

    def _extract_attributes(self, node) -> dict:
        # Add all node attributes to a dict with keys corresponding to headers
        if hasattr(node, "characteristics"):  # is material node
            attributes = self._extract_material(node)
        elif hasattr(node, "parameter_values"):  # is process node
            attributes = self._extract_process(node)
        else:  # unknown node type  # pragma: no cover
            tpl = "Node of unexpected type (not material/data nor process): {}"
            msg = tpl.format(node)
            raise WriteIsatabException(msg)
        return attributes

    def _extract_material(self, node: Material) -> dict:
        # Add all material attributes to a dict with keys corresponding to headers
        attributes = {}
        attributes[node.type] = node.name
        for characteristic in node.characteristics:
            attributes[
                self._create_labeled_name(table_headers.CHARACTERISTICS, characteristic.name)
            ] = characteristic
        for comment in node.comments:
            attributes[self._create_labeled_name(table_headers.COMMENT, comment.name)] = comment
        for factor in node.factor_values:
            attributes[self._create_labeled_name(table_headers.FACTOR_VALUE, factor.name)] = factor
        if node.material_type is not None:
            attributes[table_headers.MATERIAL_TYPE] = node.material_type
        if node.extract_label is not None:
            attributes[table_headers.LABEL] = node.extract_label
        return attributes

    def _extract_process(self, node: Process) -> dict:
        # Add all process attributes to a dict with keys corresponding to headers
        attributes = {}
        if node.protocol_ref != TOKEN_UNKNOWN:
            attributes[table_headers.PROTOCOL_REF] = node.protocol_ref
        if node.performer is not None:
            attributes[table_headers.PERFORMER] = node.performer
        if node.date is not None:
            attributes[table_headers.DATE] = node.date
        for parameter in node.parameter_values:
            attributes[
                self._create_labeled_name(table_headers.PARAMETER_VALUE, parameter.name)
            ] = parameter
        for comment in node.comments:
            attributes[self._create_labeled_name(table_headers.COMMENT, comment.name)] = comment
        if node.name_type:
            attributes[node.name_type] = node.name
        if node.array_design_ref is not None:
            attributes[table_headers.ARRAY_DESIGN_REF] = node.array_design_ref
        if node.first_dimension is not None:
            attributes[table_headers.FIRST_DIMENSION] = node.first_dimension
        if node.second_dimension is not None:
            attributes[table_headers.SECOND_DIMENSION] = node.second_dimension
        return attributes

    def _create_labeled_name(self, column_type, label):
        return "".join((column_type, "[", label, "]"))

    def write(self):
        """Write study or assay file"""
        self._ref_table = RefTableBuilder(
            self._nodes.values(),
            self._model.arcs,
            functools.partial(_is_of_starting_type, self._starting_type),
        ).run()
        self._extract_headers()
        self._write_headers()
        self._extract_and_write_nodes()


class StudyWriter(_WriterBase):
    """
    Class that writes a file from an ``Study`` object.

    :type study_or_assay: models.Study
    :param study_or_assay: The study model to write
    :type output_file: TextIO
    :param output_file: Output ISA-Tab study file
    :type quote: str
    :param quote: Optional quoting character (none by default)
    :type lineterminator: str
    :param lineterminator: Optional line terminator (OS specific by default)
    """

    #: Node type starting a study graph
    _starting_type = "Source Name"

    #: Parser for study headers
    _header_parser = StudyHeaderParser


class AssayWriter(_WriterBase):
    """
    Class that writes a file from an ``Assay`` object.

    :type study_or_assay: models.Assay
    :param study_or_assay: The assay model to write
    :type output_file: TextIO
    :param output_file: Output ISA-Tab assay file
    :type quote: str
    :param quote: Optional quoting character (none by default)
    :type lineterminator: str
    :param lineterminator: Optional line terminator (OS specific by default)
    """

    #: Node type starting an assay graph
    _starting_type = "Sample Name"

    #: Parser for assay headers
    _header_parser = AssayHeaderParser

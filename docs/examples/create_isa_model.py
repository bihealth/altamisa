# Create ISA model from scratch

import os
import sys

from altamisa.isatab import models, table_headers
from altamisa.isatab import AssayValidator, InvestigationValidator, StudyValidator
from altamisa.isatab import AssayWriter, InvestigationWriter, StudyWriter


def create_and_write(out_path):
    """Create an investigation with a study and assay and write to ``output_path``."""

    # Prepare one or more study sections
    # Prepare basic study information
    study_info = models.BasicInfo(
        path="s_minimal.txt",
        identifier="s_minimal",
        title="Germline Study",
        description=None,
        submission_date=None,
        public_release_date=None,
        comments=(
            models.Comment(name="Study Grant Number", value=None),
            models.Comment(name="Study Funding Agency", value=None),
        ),
        headers=[],
    )

    # Create one or more assays
    assay_01 = models.AssayInfo(
        measurement_type=models.OntologyTermRef(
            name="exome sequencing assay",
            accession="http://purl.obolibrary.org/obo/OBI_0002118",
            ontology_name="OBI",
        ),
        technology_type=models.OntologyTermRef(
            name="nucleotide sequencing",
            accession="http://purl.obolibrary.org/obo/OBI_0000626",
            ontology_name="OBI",
        ),
        platform=None,
        path="a_minimal.txt",
        comments=(),
        headers=[],
    )

    # Prepare one or more protocols
    protocol_01 = models.ProtocolInfo(
        name="sample collection",
        type=models.OntologyTermRef(name="sample collection"),
        description=None,
        uri=None,
        version=None,
        parameters={},
        components={},
        comments=(),
        headers=[],
    )
    protocol_02 = models.ProtocolInfo(
        name="nucleic acid sequencing",
        type=models.OntologyTermRef(name="nucleic acid sequencing"),
        description=None,
        uri=None,
        version=None,
        parameters={},
        components={},
        comments=(),
        headers=[],
    )

    # Create study object
    study_01 = models.StudyInfo(
        info=study_info,
        designs=(),
        publications=(),
        factors={},
        assays=(assay_01,),
        protocols={protocol_01.name: protocol_01, protocol_02.name: protocol_02},
        contacts=(),
    )

    # Prepare other investigation section
    # Prepare one or more ontology term source references
    onto_ref_01 = models.OntologyRef(
        name="OBI",
        file="http://data.bioontology.org/ontologies/OBI",
        version="31",
        description="Ontology for Biomedical Investigations",
        comments=(),
        headers=[],
    )

    # Prepare basic investigation information
    invest_info = models.BasicInfo(
        path="i_minimal.txt",
        identifier="i_minimal",
        title="Minimal Investigation",
        description=None,
        submission_date=None,
        public_release_date=None,
        comments=(),
        headers=[],
    )

    # Create investigation object
    investigation = models.InvestigationInfo(
        ontology_source_refs={onto_ref_01.name: onto_ref_01},
        info=invest_info,
        publications=(),
        contacts=(),
        studies=(study_01,),
    )

    # Validate investigation
    InvestigationValidator(investigation).validate()

    # Write the investigation as ISA-Tab txt file
    with open(os.path.join(out_path, investigation.info.path), "wt", newline="") as outputf:
        InvestigationWriter.from_stream(investigation=investigation, output_file=outputf).write()

    # Create a corresponding Study graph

    # Create at least on source, one sample and one collection process
    # Unique names are required for unambiguous node identification
    source_01 = models.Material(
        type="Source Name",
        unique_name="S1-source-0815",
        name="0815",
        extract_label=None,
        characteristics=(),
        comments=(),
        factor_values=(),
        material_type=None,
        headers=[table_headers.SOURCE_NAME],
    )

    sample_01 = models.Material(
        type="Sample Name",
        unique_name="S1-sample-0815-N1",
        name="0815-N1",
        extract_label=None,
        characteristics=(),
        comments=(),
        factor_values=(),
        material_type=None,
        headers=[table_headers.SAMPLE_NAME],
    )

    process_01 = models.Process(
        protocol_ref="sample collection",
        unique_name="S1-sample collection-2-1",
        name=None,
        name_type=None,
        date=None,
        performer=None,
        parameter_values=(),
        comments=(),
        array_design_ref=None,
        first_dimension=None,
        second_dimension=None,
        headers=[table_headers.PROTOCOL_REF],
    )

    # Create the arcs to connect the material and process nodes, referenced by the unique name
    arc_01 = models.Arc(tail="S1-source-0815", head="S1-sample collection-2-1")
    arc_02 = models.Arc(tail="S1-sample collection-2-1", head="S1-sample-0815-N1")

    # Create the study graph object
    study_graph_01 = models.Study(
        file=investigation.studies[0].info.path,
        header=None,
        materials={source_01.unique_name: source_01, sample_01.unique_name: sample_01},
        processes={process_01.unique_name: process_01},
        arcs=(arc_01, arc_02),
    )

    # Validate study graph
    StudyValidator(
        investigation=investigation, study_info=investigation.studies[0], study=study_graph_01
    ).validate()

    # Write the study as ISA-Tab txt file
    with open(
        os.path.join(out_path, investigation.studies[0].info.path), "wt", newline=""
    ) as outputf:
        StudyWriter.from_stream(study_or_assay=study_graph_01, output_file=outputf).write()

    # Create a corresponding Assay graph

    # Create at least on samples, one output material and one collection process
    # Unique names are required for unambiguous node identification
    # Explicit header definition per node is currently required to enable export to ISA-Tab
    sample_01 = models.Material(
        type="Sample Name",
        unique_name="S1-sample-0815-N1",
        name="0815-N1",
        extract_label=None,
        characteristics=(),
        comments=(),
        factor_values=(),
        material_type=None,
        headers=[table_headers.SAMPLE_NAME],
    )

    data_file_01 = models.Material(
        type="Raw Data File",
        unique_name="S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4",
        name="0815-N1-DNA1-WES1_L???_???_R1.fastq.gz",
        extract_label=None,
        characteristics=(),
        comments=(),
        factor_values=(),
        material_type=None,
        headers=[table_headers.RAW_DATA_FILE],
    )

    data_file_02 = models.Material(
        type="Raw Data File",
        unique_name="S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5",
        name="0815-N1-DNA1-WES1_L???_???_R2.fastq.gz",
        extract_label=None,
        characteristics=(),
        comments=(),
        factor_values=(),
        material_type=None,
        headers=[table_headers.RAW_DATA_FILE],
    )

    process_01 = models.Process(
        protocol_ref="nucleic acid sequencing",
        unique_name="S1-A1-0815-N1-DNA1-WES1-3",
        name="0815-N1-DNA1-WES1",
        name_type="Assay Name",
        date=None,
        performer=None,
        parameter_values=(),
        comments=(),
        array_design_ref=None,
        first_dimension=None,
        second_dimension=None,
        headers=[table_headers.PROTOCOL_REF, table_headers.ASSAY_NAME],
    )

    # Create the arcs to connect the material and process nodes, referenced by the unique name
    arcs = (
        models.Arc(tail="S1-sample-0815-N1", head="S1-A1-0815-N1-DNA1-WES1-3"),
        models.Arc(
            tail="S1-A1-0815-N1-DNA1-WES1-3",
            head="S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4",
        ),
        models.Arc(
            tail="S1-A1-0815-N1-DNA1-WES1_L???_???_R1.fastq.gz-COL4",
            head="S1-A1-0815-N1-DNA1-WES1_L???_???_R2.fastq.gz-COL5",
        ),
    )

    # Create the assay graph object
    assay_graph_01 = models.Assay(
        file=investigation.studies[0].assays[0].path,
        header=None,
        materials={
            sample_01.unique_name: sample_01,
            data_file_01.unique_name: data_file_01,
            data_file_02.unique_name: data_file_02,
        },
        processes={process_01.unique_name: process_01},
        arcs=arcs,
    )

    # Validate assay graph
    AssayValidator(
        investigation=investigation,
        study_info=investigation.studies[0],
        assay_info=investigation.studies[0].assays[0],
        assay=assay_graph_01,
    ).validate()

    # Create output path, if not existing
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    # Write the assay as ISA-Tab txt file
    with open(
        os.path.join(out_path, investigation.studies[0].assays[0].path), "wt", newline=""
    ) as outputf:
        AssayWriter.from_stream(study_or_assay=assay_graph_01, output_file=outputf).write()


if __name__ == "__main__":
    sys.exit(create_and_write("."))

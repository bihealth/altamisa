# Process ISA model data

from altamisa.isatab import *
import os
import warnings


# Parse and validate an investigation file
with open("i_investigation.txt", "rt") as investigation_file:
    investigation = InvestigationReader.from_stream(investigation_file).read()

InvestigationValidator(investigation).validate()


# Parse ad study and an assay file
with open("s_BII-S-1.txt", "rt") as inputf:
    study = StudyReader.from_stream("S1", inputf).read()

with open("a_transcriptome.txt", "rt") as inputf:
    assay = AssayReader.from_stream("S1", "A1", inputf).read()


# Read investigation
with open("i_investigation.txt", "rt") as investigation_file:
    investigation = InvestigationReader.from_stream(investigation_file).read()

# Validate investigation
InvestigationValidator(investigation).validate()

# Read studies and assays
path_in = os.path.normpath(os.path.dirname("i_investigation.txt"))
studies = {}
assays = {}
for s, study_info in enumerate(investigation.studies):
    if study_info.info.path:
        with open(os.path.join(path_in, study_info.info.path), "rt") as inputf:
            studies[s] = StudyReader.from_stream("S{}".format(s + 1), inputf).read()
    if study_info.assays:
        assays[s] = {}
    for a, assay_info in enumerate(study_info.assays):
        if assay_info.path:
            with open(os.path.join(path_in, assay_info.path), "rt") as inputf:
                assays[s][a] = AssayReader.from_stream(
                    "S{}".format(s + 1), "A{}".format(a + 1), inputf
                ).read()

# Validate studies and assays
for s, study_info in enumerate(investigation.studies):
    if study_info.info.path:
        StudyValidator(investigation, study_info, studies[s]).validate()
    for a, assay_info in enumerate(study_info.assays):
        if assay_info.path:
            AssayValidator(investigation, study_info, assay_info, assays[s][a]).validate()


# Write investigation
path_out = "/tmp/altamisa_example/"
os.makedirs(path_out, exist_ok=True)
with open(
    os.path.join(path_out, "i_investigation.txt"), "wt", newline=""
) as output_investigation_file:
    InvestigationWriter.from_stream(investigation, output_investigation_file).write()

# Write studies and assays
for s, study_info in enumerate(investigation.studies):
    if study_info.info.path:
        with open(os.path.join(path_out, study_info.info.path), "wt", newline="") as outputf:
            StudyWriter.from_stream(studies[s], outputf).write()
    for a, assay_info in enumerate(study_info.assays):
        if assay_info.path:
            with open(os.path.join(path_out, assay_info.path), "wt", newline="") as outputf:
                AssayWriter.from_stream(assays[s][a], outputf).write()


# Show all warnings of same type and content
warnings.simplefilter("always")

# Collect warnings
with warnings.catch_warnings(record=True) as records:
    # Work with ISA-Tab files here, e.g.:
    InvestigationValidator(investigation).validate()

# Print warnings
for record in records:
    warnings.showwarning(
        record.message, record.category, record.filename, record.lineno, record.line
    )

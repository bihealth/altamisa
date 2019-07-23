.. _examples:

========
Examples
========

Parsing and validation
----------------------

AltamISA provides separate functions to parse, validate and export ISA-tab investigation, study or
assay files, respectivly. Investigation, study and assay files may be parsed independently from each
other. Reading and validating a single investigation file is performed as follows:

.. code-block:: python

	with open("path/to/an/investigation.txt", "rt") as investigation_file:
		investigation = InvestigationReader.from_stream(investigation_file).read()
	
	InvestigationValidator(investigation).validate()
	
For study and assay parsing, unique ids need to be set to enable unambiguous identification of study
, assay and, in particular, their nodes in later applications (such as a complete graph creation):

.. code-block:: python
	
	with open("path/to/a/study_file.txt"), "rt") as inputf:
		study = StudyReader.from_stream("S1", inputf).read()
				
	with open("path/to/a/study_file.txt"), "rt") as inputf:
		assay = AssayReader.from_stream("S1", "A1", inputf).read()


However, in real use cases an ISA-Tab dataset contains related investigation, study and assay files
and thus should be handled as unit. In particular, validation of studies and assays requires
information from parent elements such as the investigation or study, respectivly. Thus, joint
parsing and validation of a complete ISA-Tab dataset may look like this:

.. code-block:: python

    # Read investigation
    with open("path/to/an/investigation.txt", "rt") as investigation_file:
        investigation = InvestigationReader.from_stream(investigation_file).read()

    # Validate investigation
    InvestigationValidator(investigation).validate()

    # Read studies and assays
    path_in = os.path.normpath(os.path.dirname("path/to/an/investigation.txt"))
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


Writing
-------

Having a set of AltamISA investigation, studies and assays available as parsed above, the models can
be given out as ISA-Tab files again as follows (make sure to not use the same path for the
investigation, as files might be overwritten otherwise):

.. code-block:: python

    # Write investigation
    with open("path/to/output/investigation.txt", "wt", newline='') as output_investigation_file:
        InvestigationWriter.from_stream(
            investigation, output_investigation_file, quote=args.quotes
        ).write()

    # Write studies and assays
    for s, study_info in enumerate(investigation.studies):
        if study_info.info.path:
            with open(os.path.join(path_out, study_info.info.path), "wt", newline="") as outputf:
                StudyWriter.from_stream(studies[s], outputf, quote=args.quotes).write()
        for a, assay_info in enumerate(study_info.assays):
            if assay_info.path:
                with open(os.path.join(path_out, assay_info.path), "wt", newline="") as outputf:
                    AssayWriter.from_stream(assays[s][a], outputf, quote=args.quotes).write()

	
Working with AltamISA warnings
------------------------------

Parsing, validating and writing of ISA-Tab files may results in AltamISA warnings, if format or data
is not conform to the specifications (except for AltamISA's :ref:`special_extensions`). Warnings
will not stop AltamISA from parsing an ISA-Tab dataset into a technically valid model. However, any
AltamISA warning should be reported to the user to allow him to improve or correct his ISA-Tab
files. Furthermore, we discourage from accepting and working with ISA-Tab datasets which result in
warnings of the category `CriticalIsaValidationWarning`.

Warnings may be collected as follows, to enable joint notification or evaluation:

.. code-block:: python

    # Show all warnings of same type and content
    if args.show_duplicate_warnings:
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

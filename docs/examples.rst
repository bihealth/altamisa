.. _examples:

========
Examples
========

To run the examples, download a full
`test dataset <https://github.com/bihealth/altamisa/tree/master/tests/data/BII-I-1>`_
(all files) from the AltamISA repository to your working directory.

Import AltamISA (if not already done) and other required modules.

.. literalinclude:: examples/process_isa_model.py
    :language: python
    :lines: 3-5


Parsing and validation
----------------------

AltamISA provides separate functions to parse, validate and export ISA-tab investigation, study or
assay files, respectivly. Investigation, study and assay files may be parsed independently from each
other. Reading and validating a single investigation file is performed as follows:

.. literalinclude:: examples/process_isa_model.py
    :language: python
    :lines: 8-12

For study and assay parsing, unique ids need to be set to enable unambiguous identification of study
, assay and, in particular, their nodes in later applications (such as a complete graph creation):

.. literalinclude:: examples/process_isa_model.py
    :language: python
    :lines: 15-20

However, in real use cases an ISA-Tab dataset contains related investigation, study and assay files
and thus should be handled as unit. In particular, validation of studies and assays requires
information from parent elements such as the investigation or study, respectively. Thus, joint
parsing and validation of a complete ISA-Tab dataset may look like this:

.. literalinclude:: examples/process_isa_model.py
    :language: python
    :lines: 23-53

Writing
-------

Having a set of AltamISA investigation, studies and assays available as parsed above, the models can
be given out as ISA-Tab files again as follows (make sure to not use the same path for the
investigation, as files might be overwritten otherwise):

.. literalinclude:: examples/process_isa_model.py
    :language: python
    :lines: 56-72


Working with AltamISA warnings
------------------------------

Parsing, validating and writing of ISA-Tab files may results in AltamISA warnings, if format or data
is not conform to the specifications (except for AltamISA's :ref:`special_extensions`). Warnings
will not stop AltamISA from parsing an ISA-Tab dataset into a technically valid model. However, any
AltamISA warning should be reported to the user to allow him to improve or correct his ISA-Tab
files. Furthermore, we discourage from accepting and working with ISA-Tab datasets which result in
warnings of the category `CriticalIsaValidationWarning`.

Warnings may be collected as follows, to enable joint notification or evaluation:

.. literalinclude:: examples/process_isa_model.py
    :language: python
    :lines: 75-87


Manual ISA model creation
-------------------------

A minimal AltamISA ISA model may be created as follows. To create more comprehensive models with, for instance, more
filled investigation sections, material or process information, please refer to the description of the
:ref:`api_models`.

.. literalinclude:: examples/create_isa_model.py
    :language: python
    :pyobject: create_and_write

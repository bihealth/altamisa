.. _manual-main:

Welcome to AltamISA's documentation!
====================================

AltamISA is a Python 3 library for representing the `ISA-tools <http://isa-tools.org/>`_ `data model <http://isa-specs.readthedocs.io/en/latest/isamodel.html>`_ and reading and writing `ISA-Tab file format <http://isa-specs.readthedocs.io/en/latest/isatab.html>`_.
The documentation is split into three parts (accessible through the navigation on the left):

Installation & Getting Started
    Instructions for the installation of the module and some examples to get you started.

API Documentation
    This section contains the API documentation for the module

Project Info
    More information on the project, including the changelog, list of contributing authors, and contribution instructions.

Quick Example
-------------

Start parsing an ISA-Tab dataset by reading and validating an
`investigation file <https://raw.githubusercontent.com/bihealth/altamisa/master/tests/data/BII-I-1/i_investigation.txt>`_
(download it to your working directory first):

.. code-block:: python

    from altamisa.isatab import *

    with open("i_investigation.txt", "rt") as investigation_file:
        investigation = InvestigationReader.from_stream(investigation_file).read()

    InvestigationValidator(investigation).validate()

For more inspiration on how to use AltamISA, see :ref:`examples`.

Features
--------

The main features are

- immutable data structures (named tuples) for representing records,
- simple implementation as directed acyclic graph (DAG) between ISA material and process nodes,
- strictly validating parser with various sanity checks,
- well-tested code, and well-documented API,
- example applications, e.g., conversion of ISA-tab to Graphviz dot.


.. _special_extensions:

Special Extensions
------------------

In addition to the original ISA-Tab format specifications, AltamISA supports
 the following special modifications to improve specific use cases:

- **List of values** in ``Characterics`` or ``Parameter Value`` fields by using
  semicolon-separators (";"). Note, for ontology terms the same number of
  splits is expected in the associated field ``Term Source REF`` and
  ``Term Accession Number``.
- **Material name** ``Library Name`` for improved library
  annotation in nucleotide sequencing assays.

.. note:: Although these modifications have been discussed by the ISA community
          (`list of values`_; `library name`_), they are not supported by
          official ISA software, yet.

.. _list of values: https://groups.google.com/forum/?hl=en-GB#!topic/isaforum/HOTScd3EeDY
.. _library name: https://groups.google.com/forum/?hl=en-GB#!topic/isaforum/yHlglEhrkI8


Frequently Asked Questions
--------------------------

Why another Python library for ISA-tab?
    Attempting to use the official Python ``isa-api`` package led to quite some frustration on our side.
    Even the official ISA-tab examples parsed into non-expected graph structures.
    Further, the official Python API has several features that were irrelevant for us, e.g., conversion from and and to various other formats.

Is validation a big deal?
    Yes it is.
    A lot of ISA-tab files that we found out in the wild while exploring the model and format were not validating.
    (We're looking at you, MetaboLights).
    The aim of the projects that we are using ISA-tab are not just describing experiments so humans can read the experiment descriptions.
    Rather, we want to have machine readable (and interpretable) data formats.
    Here, strict syntax and ideally semantic validation is key.

What's the state?
    The ISA standard and ISA-Tab file I/O is fully implemented, tested, and we're actively using it in other applications.
    The validation is also working stably yet we are planning several extensions and additional checks.

What's the aim?
    The aim is to have a stable and correct library for parsing, representing, and writing ISA-tab.

What's on the roadmap?
    Mostly fine-tuning, stabilization, and additional validations.
    At some point we might want to add support for ISA-JSON but that is a secondary aim at the moment.
    The advantage of ISA-Tab is that you can edit it with spreadsheet application.

.. toctree::
    :caption: Installation & Getting Started
    :name: getting-started
    :hidden:
    :maxdepth: 1

    installation
    getting_started
    examples

.. toctree::
    :caption: API Reference
    :name: api-reference
    :hidden:
    :maxdepth: 1
    :titlesonly:

    api_parsers
    api_writers
    api_validators
    api_models
    api_constants
    api_headers
    api_exceptions

.. toctree::
    :caption: Project Info
    :name: project-info
    :hidden:
    :maxdepth: 1
    :titlesonly:

    contributing
    authors
    history
    license

.. Generated pages, should not appear

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

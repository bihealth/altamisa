.. _manual-main:

Welcome to AltamISA's documentation!
====================================

AltamISA is a Python 3 library for representing the `ISA-tools <http://isa-tools.org/>`_ `data model <http://isa-specs.readthedocs.io/en/latest/isamodel.html>`_ and reading and writing `ISA-Tab file format <http://isa-specs.readthedocs.io/en/latest/isatab.html>`_.
AltamISA is a Python 3 library for reading and writing ISA-Tab files.
The documentation is split into three parts (accessible through the navigation on the left):

Installation & Getting Started
    Instructions for the installation of the module and some examples to get you started.

API Documentation
    This section contains the API documentation for the module

Project Info
    More information on the project, including the changelog, list of contributing authors, and contribution instructions.

Quick Example
-------------

TODO

::

    .. literalinclude:: ../examples/add_filter/add_filter.py
        :language: python


Features
--------

The main features are

- immutable data structures (named tuples) for representing records,
- simple implementation as directed acyclic graph (DAG) between ISA material and process nodes,
- strictly validating parser with various sanity checks,
- well-tested code, and well-documented API,
- example applications, e.g., conversion of ISA-tab to Graphviz dot.

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
    Reading ISA-tab works fine.
    We are extending the amount of validation in the library and plan to implement writing soon.
    Further, we have extended the model a bit here and there, e.g., for allowing lists of values and ontology terms.

What's the aim?
    The aim is to have a stable and correct library for parsing, representing, and writing ISA-tab.
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

    api_exceptions
    api_headers
    api_models
    api_parsers

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

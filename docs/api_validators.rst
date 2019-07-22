.. _api_validators:

==========
Validators
==========

Classes to validate the integrity of the investigation model as well as study
and assay graphs with respect to ISA-Tab format specifications.

AltamISA uses the `Python warnings module for reporting validation warnings <https://docs.python.org/3/library/warnings.html>`_.

.. code-block:: python

    # Parse investigation and validate, capture warnings in `ws`.
    with open("investigation.tsv", "rt") as inputf:
        with warnings.catch_warnings(record=True) as warnings:
            isa_inv = InvestigationReader.from_stream(input_file=inputf).read()
            InvestigationValidator(isa_inv).validate()

    # Iterate over all captured warnings and handle them.
    for warning in warnings:
        somehow_handle(warning)


.. note::

    You can use the :py:class:`~altamisa.exceptions.IsaWarning` class hierarchy for getting severity information.

.. contents::

altamisa.isatab.InvestigationValidator
--------------------------------------

.. autoclass:: altamisa.isatab.InvestigationValidator
    :members:

altamisa.isatab.AssayValidator
------------------------------

.. autoclass:: altamisa.isatab.AssayValidator
    :members:

altamisa.isatab.StudyValidator
------------------------------

.. autoclass:: altamisa.isatab.StudyValidator
    :members:

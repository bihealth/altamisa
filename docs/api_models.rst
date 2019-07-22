.. _api_models:

======
Models
======

Class models for storing and representing ISA data, with particular focus on ISA-Tab compatibility.
The modeling follows the structure of the specifications with different classes for each file type (investigation, study, assay), investigation sections, the different study and assay column types etc. In
particular, study and assay data (i.e. corresponding materials and processes) are represented by use of directed acyclic graphs.

Note that all models are *immutable* after construction.
Here is a common pattern for getting a *copy* with modifying select members.

.. doctest::

    >>> import attr
    >>> from altamisa.isatab import Comment
    >>> c1 = Comment(name="Name", value="the value")
    >>> c1
    Comment(name='Name', value='value')
    >>> c2 = Comment(**{**attr.asdict(c1), "name": "Another Name"})
    >>> c2
    Comment(name='Another Name', value='value')

.. contents::

altamisa.isatab.AnnotatedStr
----------------------------

.. autoclass:: altamisa.isatab.AnnotatedStr
    :members:

altamisa.isatab.OntologyTermRef
-------------------------------

.. autoclass:: altamisa.isatab.OntologyTermRef
    :members:

altamisa.isatab.Comment
-----------------------

.. autoclass:: altamisa.isatab.Comment
    :members:

altamisa.isatab.OntologyRef
---------------------------

.. autoclass:: altamisa.isatab.OntologyRef
    :members:

altamisa.isatab.BasicInfo
-------------------------

.. autoclass:: altamisa.isatab.BasicInfo
    :members:

altamisa.isatab.PublicationInfo
-------------------------------

.. autoclass:: altamisa.isatab.PublicationInfo
    :members:

altamisa.isatab.ContactInfo
---------------------------

.. autoclass:: altamisa.isatab.ContactInfo
    :members:

altamisa.isatab.DesignDescriptorsInfo
-------------------------------------

.. autoclass:: altamisa.isatab.DesignDescriptorsInfo
    :members:

altamisa.isatab.FactorInfo
--------------------------

.. autoclass:: altamisa.isatab.FactorInfo
    :members:

altamisa.isatab.AssayInfo
-------------------------

.. autoclass:: altamisa.isatab.AssayInfo
    :members:

altamisa.isatab.ProtocolComponentInfo
-------------------------------------

.. autoclass:: altamisa.isatab.ProtocolComponentInfo
    :members:

altamisa.isatab.ProtocolInfo
----------------------------

.. autoclass:: altamisa.isatab.ProtocolInfo
    :members:

altamisa.isatab.StudyInfo
-------------------------

.. autoclass:: altamisa.isatab.StudyInfo
    :members:

altamisa.isatab.InvestigationInfo
---------------------------------

.. autoclass:: altamisa.isatab.InvestigationInfo
    :members:

altamisa.isatab.Characteristics
-------------------------------

.. autoclass:: altamisa.isatab.Characteristics
    :members:

altamisa.isatab.FactorValue
---------------------------

.. autoclass:: altamisa.isatab.FactorValue
    :members:

altamisa.isatab.ParameterValue
------------------------------

.. autoclass:: altamisa.isatab.ParameterValue
    :members:

altamisa.isatab.Material
------------------------

.. autoclass:: altamisa.isatab.Material
    :members:

altamisa.isatab.Process
-----------------------

.. autoclass:: altamisa.isatab.Process
    :members:

altamisa.isatab.Arc
-------------------

.. autoclass:: altamisa.isatab.Arc
    :members:

altamisa.isatab.Study
---------------------

.. autoclass:: altamisa.isatab.Study
    :members:

altamisa.isatab.Assay
---------------------

.. autoclass:: altamisa.isatab.Assay
    :members:

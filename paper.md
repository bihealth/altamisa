---
title: 'AltamISA: a Python API for ISA-Tab files'
tags:
 - API
 - ISA-Tab
 - ISA tools
 - metadata
 - omics
 - Python
 - scientific data management
authors:
 - name: Mathias Kuhring
   orcid: 0000-0002-3287-0313
   affiliation: "1,2,3"
 - name: Mikko Nieminen
   orcid: 0000-0002-4180-8810
   affiliation: "1,3"
 - name: Jennifer Kirwan
   orcid: 0000-0002-5423-1651
   affiliation: "2,3"
 - name: Dieter Beule
   orcid: 0000-0002-3284-0632
   affiliation: "1,3"
 - name: Manuel Holtgrewe
   orcid: 0000-0002-3051-1763
   affiliation: "1,4"
affiliations:
 - name: Core Unit Bioinformatics, Berlin Institute of Health (BIH), Berlin, Germany
   index: 1
 - name: Berlin Institute of Health Metabolomics Platform, Berlin Institute of Health (BIH), Berlin, Germany
   index: 2
 - name: Max Delbrück Center (MDC) for Molecular Medicine, Berlin, Germany
   index: 3
 - name: Charité – Universitätsmedizin Berlin, Berlin, Germany
   index: 4
date: 25 July 2019
bibliography: paper.bib
---

# Introduction

AltamISA is a Python library for reading, validating, representing, and writing the ISA-Tab file format.
ISA-Tab is an open, TSV (tab separated values)-based file format for representing the ISA (investigation study assay) tools data model [@Sansone:2012].
The ISA tools data model allows for representing life science experiments and annotating the modeled objects and steps with arbitrary meta data.
The ISA tools data model and TSV format are used by various life science databases, including MetaboLights [@Haug:2013].

Shortly, the experimental process from sample extraction from a source (e.g., a donor individual) through processing of the samples to creating read-outs in one or more assays can be represented through DAGs (directed acyclic graphs) consisting of extensively annotatable so-called *material* and *process* nodes.
Together, the ISA tools data model and ISA-Tab allow for representing most conceivable experiments in life science and to store them into machine-readable files for exchanging information about such experiments.
This greatly facilitates the development of data management applications following the FAIR (findable, accessible, interoperable, and reusable, cf. @Wilkinson:2016) guidelines.

# Motivation

The authors are developing an application for managing omics data [@Nieminen:2020].
In our research regarding existing data schemas and file formats we found the ISA-Tab data model and file format to be highly suitable.
Further, it had already seen adoption by databases such as MetaboLights [@Haug:2013].

While @Sansone:2012 also maintain a Python package `isa-api` for accessing ISA-Tab data our evaluation found several issues.
To overcome these issues and to introduce several features important to us we decided to create an independent implementation of a Python library for ISA-Tab access: AltamISA.

# Aims and Features

We developed AltamISA with the aim of providing the following features:

- A strictly validating parser that is easy to extend with both validation errors and warnings.
  The importance of proper validation was underlined when we tried to test our parser with ISA-Tab sheets from MetaboLights [@Haug:2013].
  Here, a large proportion of ISA-Tab files failed validation (manual checking revealed actual problems in the data sets; data not shown).
- Standard Python exception and warning approaches to allow for user- and application-specific handling of validation issues.
- Well-tested code with good API documentation and proper examples showing the major use cases.
- Support for both reading and writing ISA-Tab files (full *round tripping*).
  This round trip operation was aimed to be *idempotent*, that is, after the first round trip any further round trip does not change the file content.
- The data structures are *immutable* (based on the `attrs` Python library).
  In particular in the connection with file access there are several advantages to this approach as one cannot accidentally change the header of the file one is reading, preventing whole classes of errors.
- All public APIs are fully annotated with Python type hints allowing for good IDE support.
  We found this particularly helpful given the large number of built-in material and process types in the ISA data model.
- The experiment DAG is implemented using a simple, graph theory--based approach with nodes representing ISA sources/samples/materials or processes and arcs explicitly connecting each.
  In our opinion, using explicit arc objects allows for a more straightforward implementation compared to storing input and output node references as done in `isa-api`.
  Further, graphs can with ease be subjected to canonical graph algorithms such as breadth-first search or union-find.

Further, we implemented a small number of example applications:

- `isa2dot` allows converting of ISA-Tab files into the DOT file format for visualization with GraphViz [@Gansner:1993].
  We found this useful for both trouble-shooting AltamISA itself and sample sheets.
- `isa2isa` allows to perform the aforementioned round tripping and thus a *normalization* of ISA-Tab files.
- `isa_validate` allows to read in an ISA-Tab file and run the AltamISA validator suite on the input.

For now, we have excluded the JSON (JavaScript Object Notation)--based file format as well as the emerging RFD (Resource Description Framework)--based file format (linkedISA [@Gonzalez:2014]) from the scope of this project.
These file formats appear to be not widely adapted and require specialized editors while ISA-Tab can be created and manipulated not only by using the ISAcreator application [@Sansone:2012] but also standard spreadsheet software.

# Summary and Conclusion

AltamISA is a practical and modern Python implementation of the ISA-Tab file model.
Besides software industry best practices such as automated tests with high test coverage, it features a comprehensive API documentation, a strictly validating parser, and an immutable data model.
It is actively maintained in connection to our data management application efforts and has been tested in practice with dozens of ISA-Tab files both prepared using the ISAcreator and spreadsheet applications.
It is our expectation that this library will be useful for other software developers who want to use the ISA model and ISA-Tab file format for file exchange.

# License and Availability

AltamISA is distributed under the MIT license and available from GitHub at https://github.com/bihealth/altamisa.
Each release is also stored to Zenodo.
The current version 0.2.0 is available with the DOI 10.5281/zenodo.3345950.
Examples and complete, up-to-date API documentation can be found at https://altamisa.readthedocs.org.
We welcome contributions via GitHub as outlined in the documentation.

# References

---
title: 'AltamISA: a Python API for ISA-Tab files'
tags:
 - scientific data management
 - django
 - framework
 - python
authors:
 - name: Mathias Kuhring
   orcid: 0000-0002-3287-0313
   affiliation: 1,2
 - name: Mikko Nieminen
   orcid: 0000-0002-4180-8810
   affiliation: 1,3
 - name: Jennifer Kirwan
   orcid: 0000-0002-5423-1651
   affiliation: 2
 - name: Dieter Beule
   orcid: 0000-0002-3284-0632
   affiliation: 1,2
 - name: Manuel Holtgrewe
   orcid: 0000-0002-3051-1763
   affiliation: 1,3
affiliations:
 - name: "Berlin Institute of Health, Anna-Louisa-Karsch-Straße 2, 10178 Berlin"
   index: 1
 - name: "Max Delbrück Center for Molecular Medicine, Robert-Rössle-Straße 10, 13125 Berlin"
   index: 2
 - name: "Charité – Universitätsmedizin Berlin, Charitéplatz 1, 10117 Berlin"
   index: 3
date: 24 July 2019
bibliography: paper.bib
---

# Introduction

The ISA-Tools framework [@Sansone:2012] defines a data model for representing an investigation with study and assay data.
Shortly, the experimental process from sample extraction from a source (e.g., a donor invidual) through processing of the samples to creating read-outs in one more more assays can be represented through DAGs (directed acyclig graphs).
Together with ISA-Tab, a TSV (tab separted values) based file format, this allows for representing most conceivable experiments in life science and store them into files for exchanging information about such experiments.
This greatly facilitates the development of data management applications following the FAIR (findable, accessible, interoperable, and reuseable, cf. @Wilkinson:2016) guidelines.

# Motivation

The authors are developing an application for managing Omics data [@Nieminen:2020].
In our research regarding existing data schemas and file formats, we found the ISA-Tab data model and file format to be highly suitable.
Further, it had already seen adoption by databases such as MetaboLights [@Haug:2013].

While @Sansone:2012 also maintain a Python package `isa-api` for accessing ISA-Tab data, an evaluation found several issues.
To overcome these issues and introducing several features important to us, we decided to create an independent implementation of a Python library for ISA-Tab access: AltamISA.

# Aims and Features

We developed AltamISA with the aim of providing the following features:

- A strictly validating parser that is easy to extend with both validation errors and warnings.
  The importance of proper validation was underlined when we tried to test our parser with ISA-Tab sheets from MetaboLights [@Haug:2013].
  A large proportion of ISA-Tab files failed validation (manual checking revealed actual problems in the data sets; data not shown).
- Well-tested code with good API documentation and proper examples showing the major use cases.
- Support for both reading and writing ISA-Tab files (full *round tripping*).
  This round trip operation was aimed to be *idempotent*, that is, after the first round trip, any further round trip does not change the file content.
- The data structures are *immutable* (based on the `attrs` Python library).
  In particular in the connection to file access there are several advantages to this approach as one cannot accidentally change the header of the file one is reading, preventing whole classes of errors.
- All public APIs are fully annotated with Python type hints, allowing for good IDE support.
  We found this particularly helpful given the large number of built-in material and process types in the ISA data model.
- The experiment DAG is implemented using a simple, graph theory--based approach with nodes representing ISA sources/samples/materials or processes and arcs explicitely connecting each.
  In our opinion, using explicit arc objects allows for a more straightforward implementation compared to storing input and output node references as done in `isa-api`.
  Further, graphs can with ease be subjected to canonical graph algorithm such as breadth-first search or union-find.

Further, we implemented a small number of example applications:

- `isa2dot` allows converting of ISA-Tab files into the DOT file format for visualization with GraphViz [@Gansner:1993].
  We found this useful for both trouble-shooting AltamISA itself and sample sheets.
- `isa2isa` allows to perform the aforementioned round tripping and thus a **normalization** of ISA-Tab files.
- `isa_validate` allows to read in an ISA-Tab file, and run the AltamISA validator suite on the input.

For now, we have excluded the emerging JSON (JavaScript Object Notation)--based linkedISA [@Gonzalez:2014] file format from the scope of this project.
This file format appears to be not widely adapted and requires specialized editors while ISA-Tab can be created and manipulated using standard spreadsheet software.

# Summary and Conclusion

AltamISA is practical and modern Python implementation of the ISA-Tab file model.
Besides software industry best practices such as automated tests with high test coverage, it features a comprehensive API documentation, a strictly validating parser, and an immutable data model.
It is actively maintained in connection to our data management application efforts and has been tested in practice with dozens of ISA-Tab files both prepared using the ISAcreator application [@Sansone:2012] and Spreadsheet applications.
It is our expectation that this library will be useful for other software developers who want to use the ISA model and ISA-Tab file format for file exchange.

# License and Availability

AltamISA is distributed under the MIT license and available from Github at https://github.com/bihealth/altamisa.
Each release is also stored to Zenodo.
The current version 0.2.0 is available with the DOI 10.5281/zenodo.3345950.
Examples and complete, up-to date API documentation can be found at https://altamisa.readthedocs.org.
We welcome contributions via Github as outlined in the documentation.

# References

[![PyPI version](https://badge.fury.io/py/altamisa.svg)](https://badge.fury.io/py/altamisa)
[![Install with Bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io)
![Continuous Integration Status](https://github.com/bihealth/altamisa/workflows/CI/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a853a56253604aa7ab87d2bcdcd9da51)](https://www.codacy.com/app/bihealth/altamisa?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/altamisa&amp;utm_campaign=Badge_Grade)
[![Coverage Badge](https://api.codacy.com/project/badge/Coverage/a853a56253604aa7ab87d2bcdcd9da51)](https://www.codacy.com/app/bihealth/altamisa?utm_source=github.com&utm_medium=referral&utm_content=bihealth/altamisa&utm_campaign=Badge_Coverage)
[![Coverage Status](https://coveralls.io/repos/github/bihealth/altamisa/badge.svg?branch=master)](https://coveralls.io/github/bihealth/altamisa?branch=master)
[![Documentation Status](https://readthedocs.org/projects/altamisa/badge/?version=latest)](https://altamisa.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.01610/status.svg)](https://doi.org/10.21105/joss.01610)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

# AltamISA

<img align="right" width="200" height="312" src="https://raw.githubusercontent.com/bihealth/altamisa/master/docs/images/Peruvian_Ragweed-small.png" />

AltamISA is an alternative implementation of [ISA-tools](http://isa-tools.org/) [data model](http://isa-specs.readthedocs.io/en/latest/isamodel.html) and [ISA-Tab file format](http://isa-specs.readthedocs.io/en/latest/isatab.html).

also:

> *Ambrosia peruviana* is a species of plant in the family Asteraceae. It occurs from Mexico south to Argentina, being common in the Antilles and the Andes.
>
> In its native range, A. peruviana is used as a medicinal plant with analgesic, antiinflammatory, anthelmintic and antiseptic properties.
>
> -- [Ambrosia peruviana, Wikipedia](https://en.wikipedia.org/wiki/Ambrosia_peruviana)

## For the Impatient

```bash
$ pip install altamisa
## OR
$ conda install altamisa
```

## What is ISA and ISA-Tab?

The ISA (Investigation-Study-Assay) defines a data model for describing life science experiments ([specification](https://isa-specs.readthedocs.io/en/latest/)).
ISA-Tab defines a file format based on TSV (tab-separated values) for storing of ISA data in files.
Shortly, experiments are encoded by DAGs (directed acyclic graphs) of samples being taken from sources (e.g., donor individuals) and then subjected to "operations" (e.g., extraction, assays, transformations) leading to different downstream "materials".

## Why AltamISA?

Attempting to use the official `isa-api` Python package in early 2018 led to quite some frustration.
Even the official ISA-tab examples parsed into non-expected graph structures.
Attempting bug fixes to `isa-api` proofed difficult because of not having complete automated tests.
Further, the scope of `isa-api` was much broader (including between ISA-Tab and other formats) such that we expected high maintenance costs (development [had apparently stalled](https://github.com/ISA-tools/isa-api/graphs/code-frequency)).

## Quick Facts

- Programming Language: Python 3 (with **full type annotations**)
- License: MIT
- Test Coverage: >90%
- Documentation: [see here](https://altamisa.readthedocs.org)
- Code Style: [black](https://github.com/python/black), 100 characters/line

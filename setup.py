#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from setuptools import find_packages, setup


def parse_requirements(path):
    """Parse ``requirements.txt`` at ``path``."""
    requirements = []
    with open(path, "rt") as reqs_f:
        for line in reqs_f:
            line = line.strip()
            if line.startswith("-r"):
                fname = line.split()[1]
                inner_path = os.path.join(os.path.dirname(path), fname)
                requirements += parse_requirements(inner_path)
            elif line != "" and not line.startswith("#"):
                requirements.append(line)
    return requirements


with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

test_requirements = parse_requirements("requirements/test.txt")
install_requirements = parse_requirements("requirements/base.txt")

package_root = os.path.abspath(os.path.dirname(__file__))
version = {}
with open(os.path.join(package_root, "altamisa/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

setup(
    author="Dieter Beule, Jennifer Kirwan, Mathias Kuhring, Manuel Holtgrewe, Mikko Nieminen",
    author_email=(
        "dieter.beule@bih-charite.de, jennifer.kirwan@bihalth.de, mathias.kuhring@bih-charite.de, "
        "manuel.holtgrewe@bih-charite.de, mikko.nieminen@bih-charite.de"
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    entry_points={
        "console_scripts": (
            "isatab2dot = altamisa.apps.isatab2dot:app",
            "isatab2isatab = altamisa.apps.isatab2isatab:app",
            "isatab_validate = altamisa.apps.isatab_validate:app",
        )
    },
    description="Implementation of ISA-tools data model and ISA-TAB",
    install_requires=install_requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="altamisa",
    name="altamisa",
    packages=find_packages(include=["altamisa*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/bihealth/altamisa",
    version=version,
    zip_safe=False,
)

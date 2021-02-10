#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from setuptools import setup, find_packages

import versioneer


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

setup(
    author="Dieter Beule, Jennifer Kirwan, Mathias Kuhring, Manuel Holtgrewe, Mikko Nieminen",
    author_email=(
        "dieter.beule@bihealth.de, jennifer.kirwan@bihalth.de, mathias.kuhring@bihealth.de, "
        "manuel.holtgrewe@bihealth.de, mikko.nieminen@bihealth.de"
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": (
            "isatab2dot = altamisa.apps.isatab2dot:main",
            "isatab2isatab = altamisa.apps.isatab2isatab:main",
            "isatab_validate = altamisa.apps.isatab_validate:main",
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
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=False,
)

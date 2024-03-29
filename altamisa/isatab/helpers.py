# -*- coding: utf-8 -*-
"""
Module for helper functions of global use.
"""


from typing import Any, List
import warnings

from ..exceptions import ParseIsatabWarning

__author__ = "Mathias Kuhring <mathias.kuhring@bih-charite.de>"


def is_ontology_term_ref(v: Any):
    """Duck typing check for objects of class `models.OntologyTermRef`"""
    return hasattr(v, "name") and hasattr(v, "ontology_name") and hasattr(v, "accession")


def list_strip(line: List[str]) -> List[str]:
    """Remove trailing space from strings in a list (e.g. a csv line)"""
    new_line = [field.strip() for field in line]
    if new_line != line:
        msg = f"Removed trailing whitespaces in fields of line: {line}"
        warnings.warn(msg, ParseIsatabWarning)
    return new_line

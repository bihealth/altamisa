# -*- coding: utf-8 -*-
"""
Module for helper functions of global use.
"""


import warnings


from ..exceptions import ParseIsatabWarning


__author__ = "Mathias Kuhring <mathias.kuhring@bihealth.de>"


def is_ontology_term_ref(v):
    """Duck typing check for objects of class `models.OntologyTermRef`"""
    return hasattr(v, "name") and hasattr(v, "ontology_name") and hasattr(v, "accession")


def list_strip(line: list):
    """Remove trailing space from strings in a list (e.g. a csv line)"""
    new_line = [field.strip() for field in line]
    if new_line != line:
        tpl = "Removed trailing whitespaces in fields of line: {}"
        msg = tpl.format(line)
        warnings.warn(msg, ParseIsatabWarning)
    return new_line

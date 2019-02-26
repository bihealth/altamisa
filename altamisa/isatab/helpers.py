# -*- coding: utf-8 -*-
"""
Module for helper functions of global use.
"""


__author__ = "Mathias Kuhring <mathias.kuhring@bihealth.de>"


def is_ontology_term_ref(v):
    """Duck typing check for objects of class `models.OntologyTermRef`"""
    return hasattr(v, "name") and hasattr(v, "ontology_name") and hasattr(v, "accession")

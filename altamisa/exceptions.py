# -*- coding: utf-8 -*-
"""Exceptions and Warnings for the Altamisa library.
"""

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class IsaException(Exception):
    """Base class for exceptions raised by monal-ISA"""


class ParseIsatabException(IsaException):
    """Exception raised on problems parsing ISA-TAB"""

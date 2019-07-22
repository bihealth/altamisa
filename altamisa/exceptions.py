# -*- coding: utf-8 -*-
"""
Exceptions and Warnings used in the AltamISA library.
"""

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"


class IsaException(Exception):
    """Base class for exceptions raised by Altamisa."""


class ParseIsatabException(IsaException):
    """Exception raised on problems parsing ISA-TAB."""


class WriteIsatabException(IsaException):
    """Exception raised on problems writing ISA-TAB."""


class IsaWarning(Warning):
    """Base class for warnings raised by Altamisa."""


class ParseIsatabWarning(IsaWarning):
    """Warning raised on problems parsing ISA-TAB."""


class WriteIsatabWarning(IsaWarning):
    """Warning raised on problems writing ISA-TAB."""


class IsaValidationWarning(IsaWarning):
    """Warning raised on problems validating ISA models or objects."""


class AdvisoryIsaValidationWarning(IsaValidationWarning):
    """Warning raised on uncritical problems when validating ISA models or objects."""


class ModerateIsaValidationWarning(IsaValidationWarning):
    """Warning raised on moderate problems when validating ISA models or objects."""


class CriticalIsaValidationWarning(IsaValidationWarning):
    """Warning raised on critical problems when validating ISA models or objects."""

import pytest

from altamisa.isatab import InvestigationForge


def test_forge(assays_investigation_file):
    # multiple studies
    with pytest.raises(IndexError):
        InvestigationForge(assays_investigation_file.name)


def test_add_assay(small_investigation_file, small2_investigation_file, assays_investigation_file):
    forge = InvestigationForge(small_investigation_file.name)
    forge.add_assay(small2_investigation_file.name)
    output = forge.investigation
    assert len(output.studies[0].assays) == 2
    assert len(output.studies[0].protocols) == 8

    # multiple studies
    with pytest.raises(IndexError):
        forge.add_assay(assays_investigation_file.name)

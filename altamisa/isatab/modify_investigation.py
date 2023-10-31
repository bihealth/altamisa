from pathlib import Path

import attr

from altamisa.isatab import InvestigationReader


class InvestigationForge:
    """
    Provides methods to add assays to an existing investigation.

    :type input_path: str | Path
    :param input_path: Location of investigation to modify.
    """

    def __init__(self, input_path: str | Path):
        i_file = Path(input_path).expanduser().resolve()

        with i_file.open("rt") as f:
            self.investigation = InvestigationReader.from_stream(f).read()

        if len(self.investigation.studies) != 1:
            # TODO: add support for multiple studies
            raise IndexError("Only single study investigations are supported.")

    @staticmethod
    def _join_protocols(x: dict, y: dict) -> dict:
        """
        Join two dicts of ISA protocols.
        For duplicate protocols, join parameter dicts.
        """
        for protocol in y:
            if protocol not in x:
                # no conflict > add protocol
                x.update({protocol: y[protocol]})
            else:
                # same protocol > check parameters
                old_parameters = x[protocol].parameters
                new_parameters = y[protocol].parameters
                for parameter in new_parameters:
                    if parameter not in old_parameters:
                        # no conflict > add parameter
                        old_parameters.update({parameter: new_parameters[parameter]})
                    else:
                        # existing parameter: raise for ontology mismatch
                        if new_parameters[parameter] != old_parameters[parameter]:
                            raise ValueError(
                                f'Ontology term mismatch for parameter "{parameter}" of protocol "{protocol}".'
                            )
        return x

    def add_assay(self, input_path: str | Path):
        """
        Add assay to investigation file.

        :type input_path: str | Path
        :param input_path: Location of investigation to modify.
        :rtype: models.InvestigationInfo
        :returns: Investigation model including all information from the investigation file.
        """
        i_file = Path(input_path).expanduser().resolve()
        with i_file.open("rt") as f:
            investigation2 = InvestigationReader.from_stream(f).read()

        if len(investigation2.studies) != 1:
            # TODO: add support for multiple studies
            raise IndexError("Only single study investigations are supported.")

        protocols = self.investigation.studies[0].protocols
        # the following will also update the investigation object
        protocols = self._join_protocols(
            protocols,
            investigation2.studies[0].protocols,
        )

        # the following will NOT update the investigation object (?)
        assays = self.investigation.studies[0].assays
        assays += investigation2.studies[0].assays

        new_study = attr.evolve(self.investigation.studies[0], protocols=protocols, assays=assays)
        self.investigation = attr.evolve(self.investigation, studies=(new_study,))

# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Experiment

Experiments are at the core of what AutoGator is built to do. 

An Experiment is a class that encapsulates all the information needed to test 
a single circuit within a GDS file. AutoGator provides a base experiment that
shows the required functions and attributes for an experiment, but it is up
to the user to implement their actual experiment. AutoGator does provide a
couple default experiments that can be used as examples as you tailor build
custom experiments. If the basic experiments provide enough functionality
for you, all the better.

In addition to Experiments, there is the concept of a Batched Experiment. This
object allows you to group a number of Circuits together and run the same
experiment on all of them. This is useful for testing a large number of
circuits in a single run. Since AutoGator has stage calibration functionality,
the researcher theoretically can begin a BatchExperiment and let the data
collection happen autonomously, without supervision, as the software will
optimize over each Circuit before performing the data collection routine.
"""

from time import sleep
from typing import Dict, Any, List

from autogator.circuit import CircuitMap
from autogator.profiles import load_default_configuration
from autogator.hardware import Stage


class Experiment:
    """
    The base Experiment prototype. The class cannot be instantiated.

    All experiments can be written expecting a :py:class:`Stage` object, setup
    according to the instance's configuration, to be available. Hence
    instruments can be accessed and used in the experiment via the
    :py:class:`Stage`.

    The experiment is instantiated once, and the same object is used to run
    every circuit in the test. So, variables will persist across runs. This
    may either be a good thing or a bad thing; variables set on the object
    in `setup()` are available in ``run()``. However, you should mainly use
    local variables in ``run()`` to avoid any unintentional data mixing.

    Attributes
    ----------
    stage : :py:class:`Stage`
        The stage object that is used to control the system.
    circuit : :py:class:`Circuit`
        The circuit currently under test.
    """

    def __init__(self) -> None:
        self._stage = None
        self._circuit = None

    @property
    def stage(self):
        return self._stage

    @property
    def circuit(self):
        return self._circuit

    def setup(self):
        pass

    def run(self):
        """
        The experiment procedure definition. 
        
        This function gets called on each Circuit. 
        """
        raise NotImplementedError

    def teardown(self):
        pass


class ExperimentRunner:
    def __init__(self, circuitmap: CircuitMap, experiment: Experiment, stage: Stage = None):
        self.circuitmap = circuitmap
        self.experiment = experiment
        self.stage = stage or load_default_configuration().get_stage()

    def run(self):
        """
        Run the experiment on all circuits in the batch.
        """
        stage = self.stage

        experiment: Experiment = self.experiment()
        experiment._stage = stage
        experiment.setup()

        for circuit in self.circuitmap.circuits:
            experiment._circuit = circuit
            stage.set_position_gds(*circuit.loc)
            experiment.run()

        experiment.teardown()

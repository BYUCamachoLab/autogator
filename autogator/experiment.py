# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Experiment
==========

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


class Experiment:
    """
    The base Experiment prototype. The class cannot be instantiated.

    All experiments can be written expecting a :py:class:`Stage` object, setup
    according to the instance's configuration, to be available. Hence
    instruments can be accessed and used in the experiment via the
    :py:class:`Stage`.

    Attributes
    ----------
    stage : :py:class:`Stage`
        The stage object that is used to control the system.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._stage = None

    @property
    def stage(self):
        return self._stage

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


class SampleExperiment(Experiment):
    def run(self):
        print("Running fake eperiment...")
        sleep(5)
        print("Done.")


class BatchExperiment:
    def __init__(self, circuitmap: CircuitMap, experiment: Experiment):
        self.circuitmap = circuitmap
        self.experiment = experiment

    def run(self):
        """
        Run the experiment on all circuits in the batch.
        """
        test_circuits = self.circuitmap.circuits
        stage = self.stage

        for circuit in test_circuits:
            print("Testing: " + str(circuit.loc))
            stage.set_position_gds(*circuit.loc)
            self.experiment.set_filename("fabrun5", circuit.loc[0], circuit.loc[1])
            # auto-optimize
            self.experiment.run()

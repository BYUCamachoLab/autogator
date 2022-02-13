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

In addition to Experiments, there is the concept of an ExperimentRunner. This
object allows you to group a number of Circuits together and run the same
experiment on all of them. This is useful for testing a large number of
circuits in a single run. Since AutoGator has stage calibration functionality,
the researcher theoretically can begin a BatchExperiment and let the data
collection happen autonomously, without supervision, as the software will
optimize over each Circuit before performing the data collection routine.
"""

from autogator.circuits import CircuitMap
from autogator.profiles import load_default_configuration
from autogator.hardware import Stage


class Experiment:
    """
    The base Experiment prototype. The class cannot be instantiated.

    All experiments can be written expecting a
    [`Stage`][autogator.hardware.Stage] object, setup according to the
    instance's configuration, to be available. Hence instruments can be
    accessed and used in the experiment via the
    [`Stage`][autogator.hardware.Stage].

    The experiment is instantiated once, and the same object is used to run
    every circuit in the test. So, variables will persist across runs. This may
    either be a good thing or a bad thing; variables set on the object in
    [`setup()`][autogator.experiments.Experiment.setup] are available in
    [`run()`][autogator.experiments.Experiment.run]. However, you should mainly
    use local variables in [`run()`][autogator.experiments.Experiment.run] to
    avoid any unintentional data mixing.

    To use this class, overload the
    [`run()`][autogator.experiments.Experiment.run] function. The optional
    [`setup()`][autogator.experiments.Experiment.setup] function is called once,
    before the experiment is run. The optional
    [`teardown()`][autogator.experiments.Experiment.teardown] function is called
    upon completion of the experiment. You can use it to clean up and close any
    instruments that were used in the experiment.

    Attributes
    ----------
    stage : Stage
        The stage object that is used to control the system.
    circuit : Circuit
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
        """
        A function that is run when the experiment runner is initialized.

        This function is called once, before the experiment is run. It is
        intended to be used to set up the experiment and the associated
        hardware. To define setup actions, override this optional function.
        """
        pass

    def run(self):
        """
        The experiment procedure definition. 
        
        This function gets called on each Circuit. Unlike
        [`setup()`][autogator.experiments.Experiment.setup], which is called
        only once by the ExperimentRunner, this function is called repeatedly;
        once for each Circuit. Note when implementing that you may want to
        optimize position over the circuit to maximize your signal. AutoGator
        does not optimize position by default, although depending on the
        accuracy of your motors, the initial move to the circuit's location
        will get you close to the signal's actual location. If you want to
        further optimize for maximum signal (recommended), you should include
        that as the first action in your experiment (consider using the default
        optimization routines provided by
        [`autogator.routines`][autogator.routines]). 
        """
        raise NotImplementedError

    def teardown(self):
        """
        A function that is run when the experiment runner is finished.

        This function is called once, after the experiment is run. It is
        intended to be used to clean up the experiment and the associated
        hardware. To define cleanup actions, override this optional function.
        """
        pass


class ExperimentRunner:
    """
    The ExperimentRunner runs an Experiment on all circuits in the batch.

    The ExperimentRunner associates a
    [`CircuitMap`][autogator.circuits.CircuitMap] with an
    [`Experiment`][autogator.experiments.Experiment]. The ``ExperimentRunner`` then
    runs sets up the experiment, sets variables on the Experiment object (such
    as stage and current circuit under test), and runs the experiment on all
    circuits in the batch. When it is complete, the ``ExperimentRunner`` tears down
    the experiment.

    Parameters
    ----------
    circuitmap : CircuitMap
        The CircuitMap that contains a list of all circuits to be tested.
    experiment : Experiment
        The testing procedure that will be executed for each circuit.
    stage : Stage, optional
        The stage object that is used to control the system. If not provided,
        the default stage is loaded from the default configuration.
    """
    def __init__(self, circuitmap: CircuitMap, experiment: Experiment, stage: Stage = None):
        self.circuitmap = circuitmap
        self.experiment = experiment
        self.stage = stage or load_default_configuration().get_stage()

    def run(self):
        """
        Blocking function that runs the Experiment on all circuits in the batch.
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

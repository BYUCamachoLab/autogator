# Experiment

Experiments, or automated testing procedures, are at the core of what AutoGator
is built to do. 

An [`Experiment`][autogator.experiments.Experiment] is a class that
encapsulates all the information needed to test a single circuit from a GDS
file. AutoGator provides a base experiment that defines the required functions
and attributes that must be overridden for an experiment, but it is up to the
user to implement their own actual experiment procedure. AutoGator's examples
do provide some basic experiments that can be used as starting points as you
tailor build custom experiments. If the basic experiments provide enough
functionality for you, all the better.

In addition to Experiments, there is the concept of an
[`ExperimentRunner`][autogator.experiments.ExperimentRunner]. This object
allows you to group a number of [`Circuit`][autogator.circuits.Circuit] objects
together and run the same experiment procedure on all of them. This is useful
for testing a large number of circuits in a single run. Since AutoGator has
stage calibration functionality, the researcher can theoretically begin an
ExperimentRunner and let the data collection happen autonomously, without
supervision, as the test procedure can include an optimization over each
Circuit before performing the data collection routine.

AutoGator uses a text file format to know about what circuits are available
to it (including a listing of all GDS coordinates). This file, represented by
the [`CircuitMap`][autogator.circuits.CircuitMap] class, can filter circuits
by user-defined parameters. The CircuitMap format is:

``` text
(<GDSx>,<GDSy>) [<param1>=<value1>, <param2>=<value2>, ...]
```

Note that &lt; &gt; denotes a required field, &lbrack; &rbrack; denotes
optional fields.

Because of AutoGator's filtering capabilities, a single text file can contain a
complete listing of all circuits on a die. The user may assign to each circuit
a parameter that defines, for example, the port ordering of lasers and
detectors for each circuit, supposing in this case that the circuit port
ordering is not consistent across the entire chip. This parameter may then be
used to group all circuits with matching configurations together to be
collectively passed to some Experiment class. Custom experiments can be written
that operate on only a subset of circuits, such as those with the same port
configuration, the ExperimentRunner can be passed that filtered CircuitMap to
enable automated. In this way, physical connections can be made (such as fiber
inputs and outputs), one set of automated tests run, a new physical connection
configured, and a different set of automated tests run.

See the [experiment example](/examples/experiment) for a basic Python
implementation.

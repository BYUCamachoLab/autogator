Hence, a single text file can contain a complete listing of all circuits on a
die. The user may assign to each circuit a parameter that defines, for example,
the port ordering of lasers and detectors for each circuit, supposing in this
case that the circuit port ordering is not consistent across the entire chip.
This parameter may then be used to group all circuits with matching
configurations together to be collectively passed to some Experiment class.
Custom experiments can be written that operate on only a subset of circuits,
and scripts that map such subsets to specific experiments to enable automated
tests can be created by the end user. Then, physical connections can be made
(such as fiber inputs and outputs), one set of automated tests run, a new
physical connection configured, and a different set of automated tests run.
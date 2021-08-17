# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Circuit Maps
------------

Circuits are a way of representing a GDS circuit with its parameters. A
CircuitMap collects a set of Circuit objects and provides methods for
sorting or filtering them by parameters.

Example
=======
Suppose I have a text file of circuits (see documentation for specification of
CircuitMap text files). I can load it into AutoGator and create a CircuitMap:

>>> p = Path(Path.home() / "Downloads/mzis.txt")
>>> cm = CircuitMap.loadtxt(p)

I can update existing (or add new) parameters in bulk:

>>> cm.update_params(submitter="sequoiac")
>>> for cir in cm:
...    cir.loc += (0, 127)

>>> cm.update_params(ports="LD")

In this example, suppose we have the Circuits from a grouping on a GDS. Suppose
this grouping is repeated six times across the file. I can create a map for the
entire GDS fild by copying CircuitMaps and adjusting its parameters.

>>> dx = 2500
>>> dy = 4200

>>> groups = [deepcopy(cm) for i in range(6)]

>>> offsets = {
...     "1": (0, 0),
...     "2": (dx, 0),
...     "3": (2*dx, 0),
...     "4": (0, dy),
...     "5": (dx, dy),
...     "6": (2*dx, dy),
... }

>>> for i, group in enumerate(groups):
...     print(len(group))
...     grouping = str(i + 1)
...     group.update_params(grouping=grouping)
...     for cir in group:
...         cir.ident = str(uuid4())
...         cir.loc += offsets[grouping]

I can then combine all the groups into a single CircuitMap:

>>> cmap = CircuitMap()
>>> for group in groups:
...     cmap += group

Now that I have a complete CircuitMap, I can export it to a text file for use
in automated tests.

>>> cmap.savetxt("updatedmzis.txt")
"""


import copy
from typing import Any, Dict, NamedTuple, Tuple, Union, List


class Circuit:
    """
    A circuit is a single isolated device from a GDS file that has a set of
    unique parameters.

    Parameters
    ----------
    loc : Location
        Location of the circuit.
    ident : str
        Unique identifier for the circuit.
    params : dict
        Key, value parameters describing the circuit. Values must all be 
        strings and are not permitted to contain spaces.
    """
    def __init__(self, loc: "Location", ident: str, params: Dict[str, str]) -> None:
        self.loc = loc
        self.ident = ident
        self.params = params

    def __str__(self) -> str:
        output = f"({self.loc.x},{self.loc.y}) {self.ident} "
        for key, val in self.params.items():
            output += f"{key}={val} "
        return output[:-1]

    def __getitem__(self, key: str) -> str:
        if type(key) is not str:
            raise TypeError("Parameter name must be a string")
        return self.params[key]

    def __setitem__(self, name: str, value: str) -> None:
        if type(name) is not str:
            raise TypeError("Parameter name must be a string")
        self.params[name] = value

    def __getattr__(self, key: str) -> str:
        if type(key) is not str:
            raise TypeError("Parameter name must be a string")
        try:
            return self.params[key]
        except KeyError as e:
            raise AttributeError(f"circuit has no attribute '{key}'")

    def __copy__(self) -> "Circuit":
        return Circuit(self.loc, self.ident, self.params.copy())

    def __deepcopy__(self, memodict: Dict[Any, Any]) -> "Circuit":
        newone = Circuit(copy.deepcopy(self.loc, memodict), self.ident, copy.deepcopy(self.params, memodict))
        return newone


class Location(NamedTuple):
    """
    Location is the GDS coordinate of a circuit as an (x, y) pair.

    Parameters
    ----------
    x : int
        X coordinate of the circuit.
    y : int
        Y coordinate of the circuit.
    """
    x: float
    y: float

    def __str__(self) -> str:
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, o: Any) -> Any:
        if isinstance(o, Location):
            return Location(self.x + o.x, self.y + o.y)
        elif isinstance(o, tuple) and len(o) == 2:
            return Location(self.x + o[0], self.y + o[1])
        else:
            raise TypeError("Cannot add Location to " + str(type(o)))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Location):
            return self.x == o.x and self.y == o.y
        elif isinstance(o, tuple) and len(o) == 2:
            return self.x == o[0] and self.y == o[1]
        else:
            return False

    def __copy__(self) -> "Location":
        return Location(self.x, self.y)

    def __deepcopy__(self, memodict: Dict[Any, Any]) -> "Location":
        return Location(self.x, self.y)


class CircuitMap:
    """
    Stores circuit objects. CircuitMaps are indexable; Circuit objects can be
    accessed by index or by location.

    Parameters
    ----------
    circuits : list
        List of Circuit objects.

    Examples
    --------
    >>> cmap = CircuitMap([Circuit(Location(0, 0), "C1", {"L": "1u", "W": "100um"})
    >>> cmap[0]
    >>> cmap[Location(0, 0)]
    >>> cmap[(0, 0)]
    """
    def __init__(self, circuits: List[Circuit]=[]) -> None:        
        self.circuits = circuits

    def __getitem__(self, key: Union[int, Location, Tuple[int, int]]) -> Circuit:
        if isinstance(key, int):
            return self.circuits[key]
        elif isinstance(key, Location):
            for circuit in self.circuits:
                if circuit.loc == key:
                    return circuit
        elif isinstance(key, tuple) and len(key) == 2:
            for circuit in self.circuits:
                if circuit.loc == Location(key[0], key[1]):
                    return circuit
        else:
            raise TypeError(f"Invalid key type '{type(key)}'")

    def __add__(self, o: "CircuitMap") -> "CircuitMap":
        if isinstance(o, CircuitMap):
            circuits = self.circuits
            for circuit in o.circuits:
                if circuit not in circuits:
                    circuits.append(circuit)
            return CircuitMap(circuits)
        else:
            raise TypeError(f"Cannot add {type(o)} to CircuitMap")

    def __str__(self) -> str:
        string = ""
        for circuit in self.circuits:
            string += str(circuit) + "\n"
        return string

    def __len__(self) -> int:
        return len(self.circuits)

    def __copy__(self) -> "CircuitMap":
        return CircuitMap(self.circuits)

    def __deepcopy__(self, memo: Any) -> "CircuitMap":
        newone = type(self)()
        newone.circuits = [copy.deepcopy(circuit) for circuit in self.circuits]
        return newone

    def filterby(self, **kwargs) -> "CircuitMap":
        """
        Filters out circuits that don't match the key, value pairs provided.
        If the key doesn't exist in a circuit, it will be filtered out.

        Parameters
        ----------
        **kwargs : dict
            The key, value pairs to filter on.

        Returns
        -------
        cmap : CircuitMap
            New CircuitMap that contains filtered circuits.

        Examples
        --------
        >>> cmap = CircuitMap.loadtxt("./sample.txt")
        >>> filtered = cmap.filterby(name="MZI1")
        """
        stepone = [c for c in self.circuits if all(hasattr(c, key) for key, val in kwargs.items())]
        filtered = [c for c in stepone if all(c[key] == val for key, val in kwargs.items())]
        cmap = CircuitMap()
        cmap.circuits = filtered
        return cmap

    def filterout(self, **kwargs) -> "CircuitMap":
        """
        Filters out any circuits that match the key, values pairs provided. If
        the circuit does not contain the given key, it will be included.

        Parameters
        ----------
        **kwargs : dict
            The key, value pairs to filter out on.

        Returns
        -------
        cmap : CircuitMap
            New CircuitMap that excludes filtered out circuits.

        Examples
        --------
        >>> cmap = CircuitMap.loadtxt("./sample.txt")
        >>> filtered = cmap.filterout(name="MZI1")
        """
        filtered = []
        for circuit in self.circuits:
            overlap = set(circuit.params.keys()).intersection(set(kwargs.keys()))
            if any(circuit[key] == kwargs[key] for key in overlap):
                continue
            filtered.append(circuit)
        cmap = CircuitMap()
        cmap.circuits = filtered
        return cmap

    def update_params(self, **kwargs) -> None:
        """
        Updates the parameters of all circuits in the CircuitMap. If the 
        paramater doesn't exist in a circuit, it will be added.

        Parameters
        ----------
        **kwargs : dict
            The key, value pairs to update the circuits with.
        """
        for circuit in self.circuits:
            for key, value in kwargs.items():
                circuit.params[key] = value

    def savetxt(self, path: str) -> None:
        """
        Saves the circuit map to a text file.

        Parameters
        ----------
        path : str
            File path to save the text file.
        """
        with open(path, "w") as f:
            for circuit in self.circuits:
                f.write(str(circuit) + "\n")

    @staticmethod
    def loadtxt(path: str):
        """
        Loads a circuit map from a text file.

        Parameters
        ----------
        path : str
            File path to the circuit map text file.

        Returns
        -------
        cmap : CircuitMap
            New CircuitMap that contains the loaded circuits.
        """
        mapfile = open(path, "r")
        circuits = []
        for line in mapfile.readlines():
            line = line.strip()
            if (line != '') and (line[0] != "#"):
                chunks = line.split()

                loc = chunks.pop(0)[1:-1]
                x, y = loc.split(",")
                ident = chunks.pop(0)
                params = dict([chunk.split("=") for chunk in chunks])

                circuit = Circuit(Location(float(x), float(y)), ident, params)
                circuits.append(circuit)
        return CircuitMap(circuits)

    def get_test_circuits(self) -> "CircuitMap":
        """
        Returns circuits that are used for stage calibration. These are 
        typically the bottom left, top left, and top right circuits of the
        GDS file.

        Returns
        -------
        test_circuits : CircuitMap
            A CircuitMap containg Circuits that have "testing_circuit=True" 
            as a parameter.
        """
        return self.filterby(testing_circuit="True")

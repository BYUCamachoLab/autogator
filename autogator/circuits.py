# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Circuit Maps

Circuits are a way of representing a GDS circuit with its parameters. A
CircuitMap collects a set of Circuit objects and provides methods for
sorting or filtering them by parameters.

## Examples

Suppose I have a text file of circuits (see documentation for specification of
CircuitMap text files). I can load it into AutoGator and create a CircuitMap:

```python
>>> p = Path(Path.home() / "Downloads/mzis.txt")
>>> cm = CircuitMap.loadtxt(p)
```

I can update existing (or add new) parameters in bulk:

```python
>>> cm.update_params(submitter="sequoiac")
>>> for cir in cm:
...    cir.loc += (0, 127)

>>> cm.update_params(ports="LD")
```

In this example, suppose we have the circuits from a grouping on a GDS. Suppose
this grouping is repeated six times across the file. I can create a map for the
entire GDS fild by copying CircuitMaps and adjusting its parameters.

```python
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
...         cir.loc += offsets[grouping]
```

I can then combine all the groups into a single CircuitMap:

```python
>>> cmap = CircuitMap()
>>> for group in groups:
...     cmap += group
```

Now that I have a complete CircuitMap, I can export it to a text file for use
in automated tests.

```python
>>> cmap.savetxt("updatedmzis.txt")
```
"""
from __future__ import annotations
import copy
import logging
from pathlib import Path
from typing import Any, Dict, NamedTuple, Tuple, Union, List

from autogator.errors import CircuitMapUniqueKeyError


log = logging.getLogger(__name__)


class Location(NamedTuple):
    """
    Location is the GDS coordinate of a circuit as an (x, y) pair.

    Typically signifies the presence of a grating coupler.

    Attributes
    ----------
    x : float
        The x coordinate of the location.
    y : float
        The y coordinate of the location.

    Examples
    --------
    >>> loc = Location(0, 0)
    >>> loc + (1, 2)
    (1, 2)
    >>> loc == (0, 0)
    True
    """
    x: float = 0
    y: float = 0

    def __str__(self) -> str:
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, o: Any) -> Any:
        """
        Locations can be added to other Locations or tuples of length 2.
        """
        if isinstance(o, Location):
            return Location(self.x + o.x, self.y + o.y)
        elif isinstance(o, tuple) and len(o) == 2:
            return Location(self.x + o[0], self.y + o[1])
        else:
            raise TypeError("Cannot add Location to " + str(type(o)))

    def __eq__(self, o: object) -> bool:
        """
        Locations can be compared to other Locations or tuples of length 2.
        """
        if isinstance(o, Location):
            return self.x == o.x and self.y == o.y
        elif isinstance(o, tuple) and len(o) == 2:
            return self.x == o[0] and self.y == o[1]
        else:
            return False

    def __copy__(self) -> Location:
        return Location(self.x, self.y)

    def __deepcopy__(self, memodict: Dict[Any, Any]) -> Location:
        return Location(self.x, self.y)


class Circuit:
    """
    A circuit is a single isolated device from a GDS file.

    Parameters
    ----------
    loc : Location
        Location of the circuit in the GDS file. Uniquely describes one 
        circuit, since multiple circuits cannot share a single location.
    params : dict
        Key, value parameters describing the circuit. Values must all be
        strings and pairs are delimited by commas.
    """
    def __init__(self, loc: Union[Tuple[float, float], Location], params: Dict[str, str]) -> None:
        self.loc = loc
        self.params = params

    @property
    def loc(self) -> Location:
        """
        Location of the circuit in the GDS file.
        """
        return self._loc

    @loc.setter
    def loc(self, loc: Union[Tuple[float, float], Location]) -> None:
        if isinstance(loc, tuple):
            loc = Location(loc[0], loc[1])
        self._loc = loc

    def __str__(self) -> str:
        output = f"({self.loc.x},{self.loc.y}) "
        for key, val in self.params.items():
            output += f"{key}={val}, "
        if self.params:
            output = output[:-2]
        return output

    def __getitem__(self, key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("Parameter name must be a string")
        return self.params[key]

    def __setitem__(self, name: str, value: str) -> None:
        if not isinstance(name, str):
            raise TypeError("Parameter name must be a string")
        self.params[name] = value

    def __getattr__(self, key: str) -> str:
        if not isinstance(key, str):
            raise TypeError("Parameter name must be a string")
        try:
            return self.params[key]
        except KeyError as exc:
            raise AttributeError(f"circuit has no attribute '{key}'") from exc

    def __copy__(self) -> Circuit:
        return Circuit(self.loc, self.params.copy())

    def __deepcopy__(self, memodict: Dict[Any, Any]) -> "Circuit":
        newone = Circuit(
            copy.deepcopy(self.loc, memodict),
            copy.deepcopy(self.params, memodict),
        )
        return newone


class CircuitMap:
    """
    Stores circuit objects. 
    
    CircuitMaps are indexable; Circuit objects can be accessed by index or by
    location.

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

    def __init__(self, circuits: List[Circuit] = []) -> None:
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
        # TODO: Implement slicing?
        # elif isinstance(key, slice):
        #     return CircuitMap(self.circuits[key])
        else:
            raise TypeError(f"Invalid key type '{type(key)}'")

    def __add__(self, o: CircuitMap) -> CircuitMap:
        """
        Adds two CircuitMaps together. Does not modify the original CircuitMap.
        """
        if isinstance(o, CircuitMap):
            circuits = self.circuits
            for circuit in o.circuits:
                if circuit not in circuits:
                    circuits.append(circuit)
            return CircuitMap(circuits)
        else:
            raise TypeError(f"Cannot add {type(o)} to CircuitMap")

    def __str__(self) -> str:
        string = "[\n"
        for circuit in self.circuits:
            string += " " + str(circuit) + "\n"
        string += "]"
        return string

    def __len__(self) -> int:
        return len(self.circuits)

    def __copy__(self) -> CircuitMap:
        return CircuitMap(self.circuits)

    def __deepcopy__(self, memo: Any) -> CircuitMap:
        newone = type(self)()
        newone.circuits = [copy.deepcopy(circuit) for circuit in self.circuits]
        return newone

    def filterby(self, **kwargs: str) -> CircuitMap:
        """
        Filters out circuits that don't match the key, value pairs provided.
        
        If the key doesn't exist in a circuit, it will be filtered out.

        Parameters
        ----------
        **kwargs : Dict[str, str]
            The key, value pairs to filter on. All parameters are interpreted
            as strings.

        Returns
        -------
        cmap : CircuitMap
            New CircuitMap that contains filtered circuits.

        Examples
        --------
        >>> cmap = CircuitMap.loadtxt("./sample.txt")
        >>> filtered = cmap.filterby(name="MZI1")
        """
        haskeys = [
            c
            for c in self.circuits
            if all(hasattr(c, key) for key in kwargs.keys())
        ]
        filtered = [
            c for c in haskeys if all(c[key] == val for key, val in kwargs.items())
        ]
        return CircuitMap(filtered)

    def filterout(self, **kwargs: str) -> CircuitMap:
        """
        Filters out any circuits that match the key, values pairs provided. 
        
        If the circuit does not contain the given key, it will be included.

        Parameters
        ----------
        **kwargs : Dict[str, str]
            The key, value pairs to filter out on. All parameters are
            interpreted as strings.

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
        return CircuitMap(filtered)

    def update_params(self, **kwargs) -> None:
        """
        Updates the parameters of all circuits in the CircuitMap. 
        
        If the parameter doesn't exist in a circuit, it will be added.

        Parameters
        ----------
        **kwargs : dict
            The key, value pairs to update the circuits with.
        """
        for circuit in self.circuits:
            for key, value in kwargs.items():
                circuit.params[key] = value

    def savetxt(self, path: Union[str, Path]) -> None:
        """
        Saves the circuit map to a text file.

        Parameters
        ----------
        path : str, Path
            File path to save the text file.
        """
        path = Path(path)
        with path.open("w") as f:
            f.write(str(self))

    @classmethod
    def loadtxt(self, filename: Union[str, Path]) -> CircuitMap:
        """
        Loads a text file containing circuit information.

        Circuit information is expected to be in the following format::
        
            (x, y) key1=value1, key2=value 2, key3=value 3, ...

        Full-line comments are allowed and are prefixed by '#'. 
        Any lines defining circuits do not support end-of-line comments.

        Parameters
        ----------
        filename : str or Path
            Name of the file to load.

        Returns
        -------
        CircuitMap
            CircuitMap containing the circuits in the file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        if isinstance(filename, str):
            filename = Path(filename)
        if not filename.exists():
            raise FileNotFoundError(f"File '{filename}' does not exist")
        circuits = []
        circuitlocs = {}
        with filename.open() as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line == "":
                    continue
                elif line.startswith("("):
                    loctxt, paramtxt = line[1:].split(")", 1)
                    loc = [float(pt.strip()) for pt in loctxt.split(",")]
                    loc = Location(*loc)
                    params = {}
                    paramtxt = paramtxt.split(",")
                    for param in paramtxt:
                        param = param.split("=")
                        params[param[0].strip()] = param[1].strip()
                    circuits.append(Circuit(loc, params))
                    if loc in circuitlocs:
                        raise CircuitMapUniqueKeyError(f"Duplicate location not allowed (lines {circuitlocs[loc]}, {i})")
                    circuitlocs[loc] = i
                else:
                    log.warning("Could not parse line %s: '%s'", i+1, line)
        return CircuitMap(circuits)

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

Using this module, you can

* read/write text representations
* select specific circuits by parameters
* track spatial locations of circuits

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
import time
import numpy as np
from pathlib import Path
from typing import Any, Dict, NamedTuple, Tuple, Union, List
from gdstk import Polygon
from collections import defaultdict
import matplotlib.pyplot as plt

from autogator.errors import CircuitMapUniqueKeyError
import gdsfactory as gf
from gdsfactory import Component

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

class PortType:
    def __init__(self, location: Location) -> None:
        self.loc = location

class Input(PortType):
    pass

class Output(PortType):
    pass

class NotUsed(PortType):
    pass

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

    def __setitem__(self, name: str, value: Any) -> None:
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
        newOne = Circuit(
            copy.deepcopy(self.loc, memodict),
            copy.deepcopy(self.params, memodict),
        )
        return newOne


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
        newOne = type(self)()
        newOne.circuits = [copy.deepcopy(circuit) for circuit in self.circuits]
        return newOne

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

    @staticmethod
    def polygonsBoundingBox(polygons):
        allPoints = np.concatenate([poly[0].points for poly in polygons])
        xMin, yMin = np.min(allPoints, axis=0)
        xMax, yMax = np.max(allPoints, axis=0)
        return ((xMin, yMin), (xMax, yMax))
    
    @staticmethod
    def isInside(polygon, boundingBox):
        # Find the polygon's and a bounding box and see if any part of the polygon's bounding box 
        # is inside the bounding box using a list comprehension
        return any(boundingBox[0][0] <= point[0] <= boundingBox[1][0] and boundingBox[0][1] <= point[1] <= boundingBox[1][1] for point in polygon.bounding_box())

    @classmethod
    def _setCircuitPorts(self, circuit: Circuit, vGroveSpacing: int, vGrovePorts: int, outputs: List[Location]) -> None:
        inputPort = circuit.loc
        ports = [Input(inputPort)]
        # Find the distances from the inputPort to the outputs
        for index in range(1, vGrovePorts):
            portPoint = vGroveSpacing*index
            result = NotUsed(portPoint)
            for output in outputs:
                if round(output.x + portPoint) == round(inputPort.x):
                    del result
                    result = Output(output)
                    break
            ports.append(result)

        if not any(isinstance(port, Output) for port in ports):
            raise RuntimeError(f'No outputs found in this circuit {circuit} at location {inputPort}. At least one output is needed.')
        circuit['ports'] = tuple(ports)


    
    @classmethod
    def _walkBack(self, startPoly, allGrates, pastComponents=[]):
        output = None
        if len(pastComponents) > 7:
            return output, pastComponents
        # if len(pastComponents) == 0:
            # plt.ion()
            # plt.show()
            # plt.clf()
            # plt.plot(*zip(*startPoly.points))

        allPolygons = self.allPolygons
        set1 = set(allPolygons)
        set2 = set(pastComponents)
        set3 = set([startPoly])
        allPolygons = list(set1-set2-set3)
        simplifiedPolygons = [poly for poly in allPolygons
                        if abs(poly.bounding_box()[0][0] - startPoly.bounding_box()[0][0]) <= 1500
                        and abs(poly.bounding_box()[0][1] - startPoly.bounding_box()[0][1]) <= 1500]

        # Find a line that we want to attach polygons to
        sharedPolys = [poly for poly in simplifiedPolygons if startPoly.contain_any(*poly.points)]
        sharedPoints = [point for poly in sharedPolys for point, isContained in zip(poly.points, startPoly.contain(*poly.points)) if isContained]

        for index, startPoint in enumerate(startPoly.points):
            if len(sharedPoints) == 0:
                break
            if not (startPoint == sharedPoints).any():
                continue
            if index >= len(startPoly.points):
                # Backup a polygon
                break
            if index == len(startPoly.points)-1:
                index = -1
            line1Distance = np.linalg.norm(startPoint - startPoly.points[index+1])
            line2Distance = np.linalg.norm(startPoint - startPoly.points[index-1])
            if line1Distance < .4 and line2Distance < .4:
                continue
            if line1Distance > 11 and line2Distance > 11:
                continue
            if len(pastComponents) > 0:
                if any(np.array_equal(startPoint, pastPoint) for pastPoint in pastComponents[-1].points):
                    continue

            for index, componentPoly in enumerate(sharedPolys):
                # plt.clf()
                # for item in pastComponents:
                #     plt.plot(*zip(*item.points))
                # plt.plot(*zip(*componentPoly.points))
                # plt.draw()
                # plt.pause(0.001)

                pastComponents.append(startPoly)
                if componentPoly in allGrates:
                    output = componentPoly
                    # plt.close()
                    break
                result, _ = self._walkBack(componentPoly, allGrates, pastComponents)
                if result is None:
                    if len(pastComponents) > 7:
                        break
                    continue
                pastComponents.append(result)
                output = result
                break
        return output, pastComponents


    @classmethod
    def _sidewaySearch(self, startGrate, vGroveSeparation) -> List[Polygon]:
        """Will look to the next grating coupler in self.gratingCouplers and then see if the spacing is correct 
        to create a circuit.

        Args:
            startGrate (_type_): One grating coupler from a circuit.


        """        
        # Find the grating couplers at the same y height as startGrate
        startGrateCenter = self.boundingBoxCenter(startGrate)
        sameHeight = [grate for grate in self.gratingCouplers 
                      if self.boundingBoxCenter(grate)[1] == startGrateCenter[1]
                      and grate is not startGrate]
        circuitCouplers = [startGrate]
        maxSeparation = 0
        for grate in sameHeight:
            nextGrateCenter = self.boundingBoxCenter(grate)
            for x in range(1,len(sameHeight)+1):
                if (round(startGrateCenter[0]) + (vGroveSeparation * x) == round(nextGrateCenter[0])
                or round(startGrateCenter[0]) - (vGroveSeparation * x) == round(nextGrateCenter[0])):
                    # Remove any duplicate polygons
                    if any(poly for poly in circuitCouplers if round(self.boundingBoxCenter(poly)[0]) == round(nextGrateCenter[0])):
                        self.gratingCouplers.remove(grate)
                    else:
                        maxSeparation = x
                        circuitCouplers.append(grate)
                    break        
        return circuitCouplers, maxSeparation    

    def polygonSearchGDS(self, polygonPoints: int) -> list:
        """Takes a GDS component and searches for polygons of a specific number of points.

        Args:
            polygonPoints (int): The number of polygon points to look for.

        Returns:
            list: A list of polygons that match the search criteria.
        """        
        matches = []
        for index, polygon in enumerate(self.allPolygons):
            if len(polygon.points) != polygonPoints:
                continue
            x, y = zip(*polygon.points)
            if not (max(abs(point - x[index-1]) for index, point in enumerate(x)) > 4):
                continue
            if not max(abs(point - y[index-1]) for index, point in enumerate(y)) > 13:
                continue
            matches.append(polygon)
        return matches

    @staticmethod
    def boundingBoxCenter(polygon):
        box = polygon.bounding_box()
        return ((box[1][0] + box[0][0])/2, (box[1][1] + box[0][1])/2)
    
    @classmethod
    def graphCircuit(self, circuitPolys):
        plt.ion()
        plt.show()
        plt.clf()
        
        for poly in circuitPolys:
            plt.plot(*zip(*poly[0].points))
            plt.draw()
        plt.pause(0.01)
    
    @classmethod
    def _createNewCircuit(self, vGroveSpacing, vGrovePorts, circuitCouplers, circuitPolygons=[]) -> Circuit:
        newCircuit = Circuit(self.boundingBoxCenter(circuitCouplers[0]), {'polygons': circuitPolygons})
        outputs = [Location(*self.boundingBoxCenter(poly)) for poly in circuitCouplers[1:]]
        self._setCircuitPorts(newCircuit, vGroveSpacing, vGrovePorts, outputs)
        return newCircuit
    
    @classmethod
    def _getCircuitPolygons(self, circuitCouplers) -> List[Polygon]:
        # Get all the points of the bounding boxes of every coupler
        circuitPoints = [point for poly in circuitCouplers for point in poly.bounding_box()]
        # Find minX minY maxX and maxY
        minX, minY = np.min(circuitPoints, axis=0)
        maxX, maxY = np.max(circuitPoints, axis=0)
        # Create a box: (min x, min y), (max x, max y) that contains the bottom right point of the right most coupler
        # And 5000 units above and to the left of that point
        box = ((minX, minY),(maxX, maxY))
        
        print('')
        startTime = time.time()
        # Simplify the self.allPolygons into a variable called simplifiedPolys that contains the polygons that are 
        # within 1500 units of the box
        simplifiedPolys = [(poly, index) for index, poly in enumerate(self.allPolygons)
                        if poly.bounding_box()[1][0] <= maxX+400
                        and poly.bounding_box()[0][0] >= minX - 400
                        and poly.bounding_box()[0][1] >= minY-50]
        endTime = time.time()
        print(f'Simplified polygons in {endTime - startTime} seconds')
        # See what polygons are inside the box and then continuously find the bounding box of those 
        # polygons until changing the bounding box stops adding polygons to the circuit
        startTime = time.time()
        while True:
            maxX = box[1][0]
            minX = box[0][0]
            maxY = box[1][1]
            minY = box[0][1]
            circuitPolygons = [poly for poly in simplifiedPolys 
                                if (poly[0].bounding_box()[1][0] <= maxX
                                and poly[0].bounding_box()[1][1] <= maxY
                                and poly[0].bounding_box()[1][0] >= minX
                                and poly[0].bounding_box()[1][1] >= minY)
                                
                                or (poly[0].bounding_box()[0][0] >= minX
                                and poly[0].bounding_box()[0][1] >= minY
                                and poly[0].bounding_box()[0][0] <= maxX
                                and poly[0].bounding_box()[0][1] <= maxY)
                                ]
            # test = [(poly, index) for index, poly in enumerate(self.allPolygons) if self.isInside(poly, box)]
            # if len(test) != len(circuitPolygons):
            #     print('no')
            if len(circuitPolygons) == 0:
                return []
            newBox = self.polygonsBoundingBox(circuitPolygons)
            if newBox == box:
                break
            box = newBox
        endTime = time.time()
        print(f'Found polygons in {endTime - startTime} seconds')

        # startTime = time.time()
        # self.graphCircuit(circuitPolygons)
        # endTime = time.time()
        # print(f'Graphed polygons in {endTime - startTime} seconds')
        return circuitPolygons

    @classmethod
    def _deletePolygons(self, polygons):
        startTime = time.time()
        indexes = set([poly[1] for poly in polygons])
        self.allPolygons = [poly for index, poly in enumerate(self.allPolygons) if index not in indexes]
        endTime = time.time()
        print(f'Deleted polygons in {endTime - startTime} seconds')

        print('\nLength of allPolygons: ', len(self.allPolygons))


    @classmethod
    def _getNextCircuit(self, vGroveSpacing, vGrovePorts) -> Union(List[Circuit], None):  
        if len(self.gratingCouplers) == 0:
            return None
        startingCoupler = self.gratingCouplers[0]
        circuitCouplers, maxUnits = self._sidewaySearch(startingCoupler, vGroveSpacing)
        # circuitPolygons = self._getCircuitPolygons(circuitCouplers)
        circuitPolygons = []
        if maxUnits > vGrovePorts-1:
            for poly in circuitCouplers: self.gratingCouplers.remove(poly)
            return self._getNextCircuit(vGroveSpacing, vGrovePorts)
        circuits = []
        if len(circuitCouplers) > 1:
            # Sort the couplers so the right most coupler is the first in the list
            circuitCouplers = sorted(circuitCouplers, key=lambda poly: self.boundingBoxCenter(poly)[0], reverse=True)
            if len(circuitCouplers) > 3:
                circuitPolygons = self._getCircuitPolygons(circuitCouplers)
                secondCircuitPolygons = self._getCircuitPolygons(circuitCouplers[1:-1])
                separate = True
                # set separate to false if secondCircuitPolygons has any polygon that are in circuit polygons
                if len(circuitPolygons) == len(secondCircuitPolygons):
                    separate = False
                if separate:
                    print('graphing new circuit')
                    self.graphCircuit(secondCircuitPolygons)
                    circuits.append(self._createNewCircuit(vGroveSpacing, vGrovePorts, circuitCouplers[1:-1], secondCircuitPolygons))
                    for coupler in circuitCouplers[1:-1]:
                        circuitCouplers.remove(coupler)
                        self.gratingCouplers.remove(coupler)
            circuits.append(self._createNewCircuit(vGroveSpacing, vGrovePorts, circuitCouplers, circuitPolygons))
            for poly in circuitCouplers: 
                self.gratingCouplers.remove(poly)
            self._deletePolygons(circuitPolygons)
            return circuits
        else:
            self.gratingCouplers.remove(startingCoupler)
            self._deletePolygons(circuitPolygons)
            return self._getNextCircuit(vGroveSpacing, vGrovePorts)
    
    @classmethod
    def loadGDS(self, vGroveSpacing: int, vGrovePorts: int, filename: Union[str, Path]) -> None:
        """Pass in a GDS file and this will build a circuit map from by looking for grating couplers in the file.

        Args:
            filename (Union[str, Path]): _description_

        Raises:
            FileNotFoundError: _description_
            CircuitMapUniqueKeyError: _description_

        Returns:
            CircuitMap: _description_
        """
        if isinstance(filename, str):
            filepath = Path(filename)
        if not filepath.exists():
            raise FileNotFoundError(f"File '{filename}' does not exist")
             
        c = gf.Component()
        self.chip = c << gf.read.import_gds(filepath)
        
        self.allPolygons = []
        seen = set()
        for poly in self.chip.parent.polygons:
            center = (self.boundingBoxCenter(poly)[0], self.boundingBoxCenter(poly)[1])
            if center in seen:
                continue
            seen.add(center)
            self.allPolygons.append(poly)
        # TODO maybe ??? look into shooting algo but it probably wont work
        # I think you'll have to either make a separate file or you need to go through circuits one by one
        # Or put this code into a generate file converter thing but even then files can vary a lot 

        # Sort polygons into a 2d array with rows being the same y value and columns being the x values
        # Have the y rows go from top to bottom and the x columns go from left to right
        # self.allPolygons = sorted(self.allPolygons, key=lambda poly: (-self.boundingBoxCenter(poly)[1], self.boundingBoxCenter(poly)[0]))
        # top = self.boundingBoxCenter(self.allPolygons[0])[1]
        # topToBottom = []
        # nextRow = []
        # for poly in self.allPolygons:
        #     polyTop = self.boundingBoxCenter(poly)[1]
        #     if polyTop == top:
        #         nextRow.append(poly)
        #     else:
        #         topToBottom.append(nextRow)
        #         top = polyTop
        #         nextRow = [poly]

        # left = self.boundingBoxCenter(self.allPolygons[0])[0]
        # leftToRight = []
        # nextRow = []
        # for poly in self.allPolygons:
        #     polyLeft = self.boundingBoxCenter(poly)[0]
        #     if polyLeft == left:
        #         nextRow.append(poly)
        #     else:
        #         leftToRight.append(nextRow)
        #         top = polyLeft
        #         nextRow = [poly]

            

        
        self.gratingCouplers = self.polygonSearchGDS(self, 126)
        self.gratingCouplers.extend(self.polygonSearchGDS(self, 124))
        self.gratingCouplers.extend(self.polygonSearchGDS(self, 166))
        self.gratingCouplers.extend(self.polygonSearchGDS(self, 228))
        # Sort polygons from top to bottom left to right
        self.gratingCouplers = sorted(self.gratingCouplers, key=lambda poly: (-self.boundingBoxCenter(poly)[1], self.boundingBoxCenter(poly)[0]))
        
        # Remove any overlapping polygons
        removeIndexes = []
        for index, poly in enumerate(self.gratingCouplers):
            if index == len(self.gratingCouplers)-1:
                break
            nextPoly = self.gratingCouplers[index+1]
            polyCenter = self.boundingBoxCenter(poly)
            nextPolyCenter = self.boundingBoxCenter(nextPoly)
            if (round(polyCenter[0]) == round(nextPolyCenter[0])
                and round(polyCenter[1]) == round(nextPolyCenter[1])):
                removeIndexes.append(self.gratingCouplers.index(nextPoly))
        self.gratingCouplers = [self.gratingCouplers[i] for i in range(len(self.gratingCouplers)) if i not in removeIndexes]
        
        print('Getting circuits')
        startTime = time.time()
        circuits = []
        while True:
            newCircuits = self._getNextCircuit(vGroveSpacing, vGrovePorts)
            if newCircuits is None:
                break
            circuits.extend(newCircuits)
        endTime = time.time()
        print(f'Found {len(circuits)} circuits in {endTime - startTime} seconds')
        

        # Get calibration circuits
        boundingBoxPoints = self.chip.get_bounding_box()
        boundingBoxPoints = [
            boundingBoxPoints[0], 
            (boundingBoxPoints[0][0], boundingBoxPoints[1][1]),
            boundingBoxPoints[1],
            (boundingBoxPoints[1][0], boundingBoxPoints[0][1]),
            ]
        # Find the polygons that are closest to the corners of the bounding box
        for index, point in enumerate(boundingBoxPoints):
            distances = [(circuit, np.linalg.norm(np.array(circuit.loc) - np.array(point))) for circuit in circuits]
            closestCircuit = min(distances, key=lambda x: x[1])[0]
            closestCircuit['calibration_circuit'] = 'True'
            if index == 2:
                break
        return CircuitMap(circuits)

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
        circuitLocs = {}
        with filename.open() as f:
            for i, line in enumerate(f):
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line == "":
                    continue
                elif line.startswith("("):
                    locTxt, paramTxt = line[1:].split(")", 1)
                    loc = [float(pt.strip()) for pt in locTxt.split(",")]
                    loc = Location(*loc)
                    params = {}
                    paramTxt = paramTxt.split(",")
                    for param in paramTxt:
                        param = param.split("=")
                        params[param[0].strip()] = param[1].strip()
                    circuits.append(Circuit(loc, params))
                    if loc in circuitLocs:
                        raise CircuitMapUniqueKeyError(f"Duplicate location not allowed (lines {circuitLocs[loc]}, {i})")
                    circuitLocs[loc] = i
                else:
                    log.warning("Could not parse line %s: '%s'", i+1, line)
        return CircuitMap(circuits)

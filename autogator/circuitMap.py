# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
Circuit & Circuit Map Classes
-------------------------------------

Circuit: Utility for storing information on a specific circuit in a gds file
Circuit Map: Utility for storing and manipulating a group of circuit objects
"""

from typing import Any, NamedTuple, overload, List

class Circuit:
    """
    Stores dictionary of information on a circuit.
    ...

    Attributes
    ----------
    params : dict
        key, word arguments of circuit information
    """
    def __init__(self):
        self.params = {}

    def __str__(self) -> str:
        output = str()
        for key in self.params:
            output += "\n" + key + ": " + str(self.params[key])
        return output

    def __getattr__(self, key):
        return self.params[key]

    # Adds a parameter
    def add_param(self, key, value):
        self.params[key] = value


class Location(NamedTuple):
    """
    Stores x and y coordinate of a location.
    """
    x: float
    y: float
    def __str__(self) -> str:
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class CircuitMap:
    """
    Stores circuit objects.
    ...

    Attributes
    ----------
    text_file_path : str
        Direct file path to text file of circuits to be parsed into a CircuitMap 
    """
    def __init__(self, text_file_path: str = None):
        if text_file_path == None:
            return

        circuitMap_file = open(text_file_path, "r")
        circuitMap_circuits = []

        for line in circuitMap_file:
            if line is not None:
                line = line[:-1]
                new_circuit = Circuit()
                chunks = line.split(" ")  
                location = chunks.pop(0)  
                coordinates = location.split(",")  
                coordinates[0] = (coordinates[0])[1:]  
                coordinates[1] = (coordinates[1])[:-1]  
                new_circuit.add_param("location", Location(float(coordinates[0]), float(coordinates[1])))  
                ID = chunks.pop(0)  
                new_circuit.add_param("ID", ID)  

                for chunk in chunks:
                    keyValues = chunk.split("=")
                    new_circuit.add_param(keyValues[0], keyValues[1])
                circuitMap_circuits.append(new_circuit)

        self.circuits = circuitMap_circuits

    def __add__(self, o: Any) -> Any:
        joined_circuits = []
        for circuit in self.circuits:
            if circuit not in joined_circuits:
                joined_circuits.append(circuit)
        for circuit in o.circuits:
            if circuit not in joined_circuits:
                joined_circuits.append(circuit)
        circuitMap = CircuitMap()
        circuitMap.set_circuits(joined_circuits)
        return circuitMap

    def __str__(self) -> str:
        string = ""
        for x in self.circuits:
            for key, value in x.params.items():
                string += key + "=" + str(value) + " "
            string += "\n"
        return string

    # Filters map to only include circuits with a specific value for a specific key
    def filter(self, **kwargs) -> Any:
        """
        Filters CircuitMap to only include circuits that match the key, values pairs provided.

        .. note:: Will disclude circuits that don't contain the given key

        Parameters
        ----------
        **kwargs : **kwargs
            The key, value pairs to filter on.

        Returns
        -------
        circuitMap : CircuitMap
            New CircuitMap that contains filtered circuits.
        """
        starting_circuits = self.get_circuits()
        for key, value in kwargs.items():
            filtered_circuits = []
            for circuit in starting_circuits:
                if key in circuit.params.keys():
                    valueInCircuit = circuit.params.get(key, 0)
                    if str(valueInCircuit) == str(value):
                        filtered_circuits.append(circuit)
            starting_circuits.clear()
            starting_circuits.extend(filtered_circuits)
        circuitMap = CircuitMap()
        circuitMap.set_circuits(filtered_circuits)
        return circuitMap

    # Filters map to exclude circuits with a specific value for a specific key
    def filter_out(self, **kwargs) -> Any:
        """
        Filters CircuitMap to exclude circuits that match the key, values pairs provided.

        .. note:: Will include circuits that don't contain the given key.

        Parameters
        ----------
        **kwargs : **kwargs
            The key, value pairs to filter out on.

        Returns
        -------
        circuitMap : CircuitMap
            New CircuitMap that excludes filtered out circuits.
        """
        starting_circuits = self.get_circuits()
        for key, value in kwargs.items():
            filtered_circuits = []
            for circuit in starting_circuits:
                if key in circuit.params.keys():
                    valueInCircuit = circuit.params.get(key, 0)
                    if str(valueInCircuit) != str(value):
                        filtered_circuits.append(circuit)
                else:
                    filtered_circuits.append(circuit)
            starting_circuits.clear()
            starting_circuits.extend(filtered_circuits)
        circuitMap = CircuitMap()
        circuitMap.set_circuits(filtered_circuits)
        return circuitMap

    # Adds a new parameter to the circuits in the circuitMap
    def add_new_param(self, **kwargs) -> Any:
        """
        Adds new parameters to each circuit in CircuitMap based on key, value pairs provided.

        Parameters
        ----------
        **kwargs : **kwargs
            The key, value pairs to add as parameters.

        Returns
        -------
        circuitMap : CircuitMap
            New CircuitMap whos circuits includes new parameters.
        """
        new_circuits = []
        for circuit in self.circuits:
            # Gets the Arguments in the function call and adds them to the circuit
            for key, value in kwargs.items():
                circuit.add_param(key, value)
            new_circuits.append(circuit)
        circuitMap = CircuitMap()
        circuitMap.set_circuits(new_circuits)
        return circuitMap

    # Sets the circuits of the CircuitMap
    def set_circuits(self, circuits: List[Circuit]) -> None:
        """
        Sets the list of circuits in CircuitMap to provided list.

        Parameters
        ----------
        circuits : List[Circuit]
            List of circuits to set to CircuitMap.
        """
        self.circuits = circuits

    # Returns the the circuits in the circuitMap
    def get_circuits(self) -> List[Circuit]:
        """
        Returns to list of circuits in CircuitMap.

        Returns
        -------
        circuits : List[Circuit]
            List of circuits in CircuitMap.
        """
        return self.circuits

    # Returns single circuit with specific value for a specific key
    # Defaults to ID key
    def get_circuit(self, key: str = "ID", value: str = "") -> Circuit:
        """
        Returns circuit that matches key, value pair provided.

        .. note:: Will return first instance found if multiple matches exist.

        Parameters
        ----------
        key : str, default="ID"
            Key of the parameter a value is being matched to.
        value : str, default=""
            Value of parameter that is being searched for.

        Returns
        -------
        circuit : Circuit
            List of circuits in CircuitMap.
        """
        for circuit in self.circuits:
            valueInCircuit = circuit.params.get(key, 0)
            if valueInCircuit == value:
                return circuit
        return None

    # Returns test circuits for calibration
    # Very left, bottom
    # Very top, left
    # Very right, top
    # Based on coordinates
    def get_test_circuits(self) -> List[Circuit]:
        return self.filter(testing_circuit="True").get_circuits()
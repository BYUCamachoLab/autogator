from typing import Any, NamedTuple, overload


class Circuit:
    def __init__(self):
        self.params = {}

    def __str__(self) -> str:
        output = str()
        for key in self.params:
            output += "\n" + key + ": " + str(self.params[key])
        return output

    def __getattr__(self, key):
        return self.params[key]

    def add_param(self, key, value):
        self.params[key] = value


class Location(NamedTuple):
    x: float
    y: float

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Map:
    def __init__(self, text_file: str = None):
        if text_file == None:
            return
        mapFile = open(text_file, "r")
        circuitsForMap = []

        for line in mapFile:
            if line is not None:
                line = line[:-1]
                newCircuit = Circuit()
                chunks = line.split(" ")
                location = chunks.pop(0)
                coordinates = location.split(",")
                coordinates[0] = (coordinates[0])[1:]
                coordinates[1] = (coordinates[1])[:-1]
                newCircuit.add_param(
                    "location", Location(float(coordinates[0]), float(coordinates[1]))
                )

                ID = chunks.pop(0)
                newCircuit.add_param("ID", ID)

                for chunk in chunks:
                    keyValues = chunk.split("=")
                    newCircuit.add_param(keyValues[0], keyValues[1])
                circuitsForMap.append(newCircuit)
        self.circuits = circuitsForMap

    def __add__(self, o: Any) -> Any:
        joined_circuits = []
        for circuit in self.circuits:
            if circuit not in joined_circuits:
                joined_circuits.append(circuit)
        for circuit in o.circuits:
            if circuit not in joined_circuits:
                joined_circuits.append(circuit)
        map = Map()
        map.set_circuits(joined_circuits)
        return map

    def __str__(self) -> str:
        string = ""
        for x in self.circuits:
            for key, value in x.params.items():
                string += key + "=" + str(value) + " "
            string += "\n"
        return string

    def filter(self, key: str, value: Any) -> Any:
        filtered_circuits = []
        for x in self.circuits:
            valueInCircuit = x.params.get(key, 0)
            if str(valueInCircuit) == str(value):
                filtered_circuits.append(x)
        map = Map()
        map.set_circuits(filtered_circuits)
        return map

    def filter_out(self, key: str, value: Any) -> Any:
        filtered_out_circuits = []
        for x in self.circuits:
            valueInCircuit = x.params.get(key, 0)
            if str(valueInCircuit) != str(value):
                filtered_out_circuits.append(x)
        map = Map()
        map.set_circuits(filtered_out_circuits)
        return map

    def filter_by_group(self, group: int = None) -> Any:
        filtered_circuits = []
        for circuit in self.circuits:
            valueInCircuit = circuit.params.get("ID", 0)
            if "grouping_" + str(group) in valueInCircuit:
                filtered_circuits.append(circuit)
        map = Map()
        map.set_circuits(filtered_circuits)
        return map

    def addNewParam(self, **kwargs) -> Any:
        new_circuits = []
        for circuit in self.circuits:
            for key, value in kwargs.items():
                circuit.add_param(key, value)
            new_circuits.append(circuit)
        map = Map()
        map.set_circuits(new_circuits)
        return map

    # Sets the circuits of the Map
    def set_circuits(self, circuits: list[Circuit]) -> None:
        self.circuits = circuits

    # Returns the the circuits in the map
    def get_circuits(self) -> list[Circuit]:
        return self.circuits

    # Gets a specific item in the circuit using the ID
    def get_circuit(self, key: str = "ID", value: str = "") -> Circuit:
        for circuit in self.circuits:
            valueInCircuit = circuit.params.get(key, 0)
            if valueInCircuit == value:
                return circuit
        return None

    # Gets the Test Circuit Components
    def get_test_circuits(self) -> list[Circuit, Circuit, Circuit]:
        # Empty Result
        test_circuits = [self.circuits[0], self.circuits[0], self.circuits[0]]

        # Iterates through every circuit contained in the map
        for circuit in self.circuits:
            # Tests to see if the current circuit is in the bottom left of the chip
            if test_circuits[0] != None:
                if test_circuits[0].location.y > circuit.location.y:
                    test_circuits[0] = circuit
                elif test_circuits[0].location.y == circuit.location.y:
                    if test_circuits[0].location.x > circuit.location.x:
                        test_circuits[0] = circuit
            else:
                test_circuits[0] = circuit

            # Tests to see if the current circuit is in the top left of the chip
            if test_circuits[1] != None:
                if test_circuits[1].location.y < circuit.location.y:
                    test_circuits[1] = circuit
                elif test_circuits[1].location.y == circuit.location.y:
                    if test_circuits[1].location.x > circuit.location.x:
                        test_circuits[1] = circuit
            else:
                test_circuits[1] = circuit

            # Tests to see if the current circuit is in the top right of the chip
            if test_circuits[2] != None:
                if test_circuits[2].location.y < circuit.location.y:
                    test_circuits[2] = circuit
                elif (
                    test_circuits[2].location.y == circuit.location.y
                    and test_circuits[1] != circuit
                ):
                    if test_circuits[2].location.x < circuit.location.x:
                        test_circuits[2] = circuit
            else:
                if test_circuits[1] != circuit:
                    test_circuits[2] = circuit
        return test_circuits

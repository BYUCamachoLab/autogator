from typing import Any, NamedTuple, overload


class Circuit:
    def __init__(self):
        # Dynamic Parameters
        self.params = {}

    # String Result
    def __str__(self) -> str:
        output = str()
        for key in self.params:
            output += "\n" + key + ": " + str(self.params[key])
        return output

    # Gets and attribute associated with the key
    def __getattr__(self, key):
        return self.params[key]

    # Adds a parameter
    def add_param(self, key, value):
        self.params[key] = value


class Location(NamedTuple):
    # Coordinates
    x: float
    y: float

    # string result
    def __str__(self) -> str:
        return "(" + str(self.x) + ", " + str(self.y) + ")"


class Map:
    def __init__(self, text_file: str = None):
        # Returns an empty map if no text_file is provided
        if text_file == None:
            return

        # Opens the file
        map_file = open(text_file, "r")
        map_circuits = []

        # Adds in each circuit listed in the text file
        for line in map_file:
            if line is not None:
                line = line[:-1]  # Takes out the '\n'
                new_circuit = Circuit()
                chunks = line.split(
                    " "
                )  # Splits up all the properties of the circui in the text file
                location = chunks.pop(0)  # Retrieves the coordinate properties
                coordinates = location.split(",")  # Seperates the x and y coordinates
                coordinates[0] = (coordinates[0])[
                    1:
                ]  # drops the '(' and gets the x coordinate
                coordinates[1] = (coordinates[1])[
                    :-1
                ]  # drops the ')' ang gets the y coordinate
                new_circuit.add_param(
                    "location", Location(float(coordinates[0]), float(coordinates[1]))
                )  # Creates a new location object, containing the x and y coordinates

                ID = chunks.pop(0)  # Gets the ID chunk
                new_circuit.add_param("ID", ID)  # The ID as new parameter

                # The Remaining chunks are individually processed into the circuit
                for chunk in chunks:
                    keyValues = chunk.split("=")
                    new_circuit.add_param(keyValues[0], keyValues[1])
                map_circuits.append(new_circuit)
        self.circuits = map_circuits

    # Overloads the + operator to combine this map's circuits with another map's circuits
    # Acts as a full join, with only unique elements
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

    # The String Result of this class
    def __str__(self) -> str:
        string = ""
        for x in self.circuits:
            for key, value in x.params.items():
                string += key + "=" + str(value) + " "
            string += "\n"
        return string

    # Gets every circuit that is not filtered out and returns a new map
    def filter(self, key: str, value: Any) -> Any:
        filtered_circuits = []
        for circuit in self.circuits:
            valueInCircuit = circuit.params.get(key, 0)
            if str(valueInCircuit) == str(value):
                filtered_circuits.append(circuit)
        map = Map()
        map.set_circuits(filtered_circuits)
        return map

    # Gets every circuit that is filtered out and returns a new map
    def filter_out(self, key: str, value: Any) -> Any:
        filtered_out_circuits = []
        for circuit in self.circuits:
            valueInCircuit = circuit.params.get(key, 0)
            if str(valueInCircuit) != str(value):
                filtered_out_circuits.append(circuit)
        map = Map()
        map.set_circuits(filtered_out_circuits)
        return map

    def simple_search(self, search_argument: str) -> Any:
        filtered_circuits = []
        for circuit in self.circuits:
            # Gets the ID which contains the group
            circuit_id = circuit.params.get("ID", 0)
            # Checks the ID for the group
            if search_argument in circuit_id:
                filtered_circuits.append(circuit)
        map = Map()
        map.set_circuits(filtered_circuits)
        return map

    def search(self, search_argument: str) -> Any:
        # Seperates the search groups we want
        search_clusters = search_argument.lower().strip().split(",")
        # an output list
        filtered_circuits = []
        # Goes through the different sets of circuits desired
        for search_cluster in search_clusters:
            # performs a search on inclusive and exclusive parameters
            filtered_circuits.extend(self.sub_search(search_cluster))
        # Makes the list unique
        filtered_circuits = list(set(filtered_circuits))

        # Produces a map that contains the circuits
        map = Map()
        map.set_circuits(filtered_circuits)
        return map

    def sub_search(self, search_argument: str) -> list:
        # An output list
        filtered_circuits = []
        # The desried search terms appended to negative terms
        positive_terms = search_argument.strip().split("+")
        for circuit in self.circuits:
            meets_criteria = True
            # Iterates through the desired terms
            for search_terms in positive_terms:
                # Splits up the terms, the desired term will be on the left
                terms = search_terms.strip().split("-")
                # Gets the desired term
                positive_term = terms[0].strip()
                # Gets any appended excluded terms
                negative_terms = []
                if len(terms) > 1:
                    negative_terms = terms[1:]
                # Gets the ID which contains the circuit type
                circuit_id = circuit.params.get("ID", 0)
                # Checks if the ID conatins the positive search term
                if positive_term in circuit_id.lower():
                    for negative_term in negative_terms:
                        if negative_term.strip() in circuit_id.lower():
                            meets_criteria = False
                            break
                else:
                    meets_criteria = False
                    break
            # If the
            if meets_criteria:
                filtered_circuits.append(circuit)

        return filtered_circuits

    # Returns a map with every circuit in this map that are in the specified group
    def filter_by_group(self, group: int = None) -> Any:
        filtered_circuits = []
        for circuit in self.circuits:
            # Gets the ID which contains the group
            valueInCircuit = circuit.params.get("ID", 0)
            # Checks the ID for the group
            if "grouping_" + str(group) in valueInCircuit:
                filtered_circuits.append(circuit)
        map = Map()
        map.set_circuits(filtered_circuits)
        return map

    # Adds a new parameter to the circuits in the map
    def add_new_param(self, **kwargs) -> Any:
        new_circuits = []
        for circuit in self.circuits:
            # Gets the Arguments in the function call and adds them to the circuit
            for key, value in kwargs.items():
                circuit.add_param(key, value)
            new_circuits.append(circuit)
        map = Map()
        map.set_circuits(new_circuits)
        return map

    # Sets the circuits of the Map
    def set_circuits(self, circuits: list[Circuit]) -> None:
        circuits.sort(key=lambda circuit: circuit.ID, reverse=False)
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

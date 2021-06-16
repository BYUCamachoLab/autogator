from typing import NamedTuple

class Circuit:
    def __init__(self):
        self.params = {}

    def __getattr__(self, key):
        return self.params[key]

    def add_param(self, key, value):
        self.params[key] = value


class Location(NamedTuple):
    x: float
    y: float  


class Map:
    def __init__(self, fileName):
        mapFile = open(fileName, 'r')
        circuitsForMap = []

        for line in mapFile:
            if line is not None:
                line = line[:-1]
                newCircuit = Circuit()
                chunks = line.split(" ")
                location = chunks.pop(0)
                coordinates = location.split(',')
                coordinates[0] = (coordinates[0])[1:]
                coordinates[1] = (coordinates[1])[:-1]
                newCircuit.add_param("location", Location(coordinates[0], coordinates[1]))

                ID = chunks.pop(0)
                newCircuit.add_param("ID", ID)

                for chunk in chunks:
                    keyValues = chunk.split("=")
                    newCircuit.add_param(keyValues[0], keyValues[1])
                circuitsForMap.append(newCircuit)        
        self.circuits = circuitsForMap

    def __add__(self, map2):
        for x in map2.circuits:
            self.circuits.append(x)
        return self

    def __str__(self):
        string = ""
        for x in self.circuits:
            for key, value in x.params.items():
                string += key + "=" + str(value) + " "
            string += "\n"
        return string

    def filter(self, key, value):
        newCircuits = []
        for x in self.circuits:
            valueInCircuit = x.params.get(key, 0)
            if valueInCircuit == value:
                newCircuits.append(x)
        self.circuits = newCircuits
        return self    

    def filter_out(self, key, value):
        newCircuits = []
        for x in self.circuits:
            valueInCircuit = x.params.get(key, 0)
            if valueInCircuit != value:
                newCircuits.append(x)
        self.circuits = newCircuits
        return self   
        
    def addNewParam(self, **kwargs):
        newCircuits = []
        for x in self.circuits:
            for key, value in kwargs.items():
                x.add_param(key, value)
            newCircuits.append(x)
        self.circuits = newCircuits
        return self

    def return_circuits(self):
        return self.circuits
    
    # Gets a specific item in the circuit using the ID
    def get_circuit(self, key: str="ID", value: str="") -> Circuit:
        for circuit in self.circuits:
            valueInCircuit = circuit.params.get(key, 0)
            if valueInCircuit == value:
                return circuit
        return None

import gdstk


# Substring known to be found in grading cupler cells
GC_STRING = "gc"

GDS_FILE = "fabrun5.gds"

# End class for each Circuit
class Circuit:
    def __init__(self, name="", origin=[0, 0], ports=""):
        self.name = name
        self.origin = origin
        self.ports = ports

    def find_second_name(self):
        return (self.name[self.name.rindex(":") + 1 :])[:-2]

    def print(self):
        return (
            "("
            + str(self.origin[0])
            + ","
            + str(self.origin[1])
            + ") "
            + self.name
            + " name="
            + self.find_second_name()
            + " ports="
            + self.ports
            + " mode=TE submitter='sequoiac'"
        )


# Each cell is stored by name with their references and whether or not they are a circuit
class Dependency:
    def __init__(self, refs=[], isCircuit=False, name=""):
        self.refs = refs
        self.isCircuit = isCircuit
        self.name = name


# Working Class for creating circuit objects
class Unit:
    def __init__(self, name="", origin=[]):
        self.name = name
        self.origin = origin

    def __str__(self):
        return self.name + ": (" + str(self.origin[0]) + "," + str(self.origin[1]) + ")"


# More simple version of Dependeny
class RefObject:
    def __init__(self, name="", origin=[]):
        self.name = name
        self.origin = origin


# Test if cell is circuit by if it contains a Grading Cupler in its references
def contains_GC(cell):
    references = cell.references
    for i in references:
        if GC_STRING in str(i):
            return True
    return False


# Getting name from toString property of gdstk reference object
def get_name(referenceString):
    string = str(referenceString)[19:]
    num = string.find("'")
    string = string[:num]
    return string


# Creating reference objects for a given cell
def create_ref_objects(cell, namesUsed):
    RefObjects = []
    refs = cell.references
    for i in refs:
        refName = get_name(i)
        num = 1
        while (refName + "_" + str(num)) in namesUsed:
            num += 1
        RefObjects.append(RefObject((refName + "_" + str(num)), i.origin))
        namesUsed.append((refName + "_" + str(num)))
    return RefObjects


# Recursive algorithm that progressively attaches cell references on top of each other from the base cell
# Up until it reaches a cell that is a circuit, then it stops and appends the data into a circuit object
def dig(Units, dependencies, circuits, isFirst):
    newUnits = []
    nameToFind = ""
    for i in Units:
        if isFirst:
            nameToFind = i.name[:-2]
        else:
            nameToFind = i.name[i.name.rindex(":") + 1 :]
            nameToFind = nameToFind[:-2]
        dependencyMatch = [x for x in dependencies if x.name == nameToFind]
        if len(dependencyMatch) != 0:
            if dependencyMatch[0].isCircuit:
                ports = ""
                for j in dependencyMatch[0].refs:
                    if "gc" in j.name:
                        ports += "D"
                alreadyInList = [x for x in circuits if x.name == i.name]
                if len(alreadyInList) == 0:
                    circuits.append(Circuit(i.name, i.origin, ports))
            else:
                for j in dependencyMatch[0].refs:
                    if len(j.name) > 5:
                        newUnit = Unit(
                            (i.name + "::" + j.name),
                            [i.origin[0] + j.origin[0], i.origin[1] + j.origin[1]],
                        )
                        newUnits.append(newUnit)
            dig(newUnits, dependencies, circuits, False)
        else:
            print("Could not find match")


def run():
    # Library to Read
    lib = gdstk.read_gds(GDS_FILE)
    lib1 = lib.cells

    # Initialize Array for storing Circuits
    circuits = []
    # Initialize Array that will be used to make sure all names are unique
    namesUsed = []

    dependencies = []

    # Populate dependencies list with dependency objects for each type of cell
    cells = lib1[-1].dependencies(True)
    for i in cells:
        if contains_GC(i):
            dependencies.append(
                Dependency(create_ref_objects(i, namesUsed), True, i.name)
            )
        else:
            dependencies.append(
                Dependency(create_ref_objects(i, namesUsed), False, i.name)
            )

    # Calculating starting Cells to build off of
    Units = []
    UnitsEdge = []
    beforeUnits = lib1[-1].references
    beforeUnits = [x for x in beforeUnits if len(get_name(x)) > 2]
    beforeUnits = [
        x for x in beforeUnits if "gc" not in get_name(x) and "Wave" not in get_name(x)
    ]

    for i in beforeUnits:
        if str(i.repetition) != "No Repetition":
            rows = i.repetition.rows
            columns = i.repetition.columns
            spacing = i.repetition.spacing
            origin = i.origin
            num = 1
            for c in range(columns):
                for r in range(rows):
                    Units.append(
                        Unit(
                            get_name(i) + "_" + str(num),
                            [
                                i.origin[0] + (c * spacing[0]),
                                i.origin[1] + (r * spacing[1]),
                            ],
                        )
                    )
                    num = num + 1
        else:
            Units.append(Unit(get_name(i), i.origin))

    dig(Units, dependencies, circuits, True)

    f = open("circuits.txt", "w")
    for h in circuits:
        f.write(h.print() + "\n")
    f.close()

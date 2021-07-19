from autogator.circuitMap import CircuitMap

circuitMap = CircuitMap("circuits_test.txt")
print("This is every circuit on the chip")
print(circuitMap)
print()

input("Press Enter to see calibration circuits")
# gets Circuits used for calibration
test_circuits = circuitMap.get_test_circuits()
print(test_circuits[0])
print(test_circuits[1])
print(test_circuits[2])
print()

input("Press Enter to see filtered circuits")
# Shows the filtering function
circuitMap2 = circuitMap.filter("ports", "DDDDD")
print(circuitMap2)
print()

input("Press Enter to see multi-filtered circuits")
# Multilayered Filter
circuitMap2 = circuitMap.filter("ports", "DDDDD").filter("name", "SIOH_jogs_0")
print(circuitMap2)
print()

input("Press Enter to circuit parameters added")
# Shows the Ability Add New Parameters, adding parameters will alter the original circuit circuitMap
circuitMap2 = circuitMap2.add_new_param(type="Yellow", flavor="panda")
print(circuitMap2)
print()
input("Press Enter to see that it Changes the circuitMap also")
print(circuitMap.filter("name", "SIOH_jogs_0"))
print()

input("Press Enter to see the overloaded + operator act as an exclusive join")
# Performs a join only returning unique items so circuitMap3 == circuitMap
circuitMap3 = circuitMap + circuitMap2
print(circuitMap3)
print()

input("Press Enter to see the overloaded + operator act as an exclusive join")
# Shows the join work with two circuitMaps that do not contain the same circuits
circuitMap3 = circuitMap.filter("name", "SIOH_jogs_1") + circuitMap2
print(circuitMap3)
print()

input("Press Enter to see filtered by group")
# Shows how to filter by group number
circuitMap4 = circuitMap.filter_by_group(4)
print(circuitMap4)
print()

input("Press Enter to see a group parameter added")
# Shows why adding params could be useful, we can filter to get specific circuits and then add in a parameter specific to them
circuitMap4.add_new_param(group=4)
print(circuitMap4)
print()

input("Press Enter to see filtered by group using the new group parameter")
# It is then searchable by the new parameter
circuitMap5 = circuitMap.filter("group", "4")
print(circuitMap5)
print()

input("Press Enter to see every group with a group parameter")
# Now every group can be searched by a normal filter
circuitMap.filter_by_group(1).add_new_param(group=1)
circuitMap.filter_by_group(2).add_new_param(group=2)
circuitMap.filter_by_group(3).add_new_param(group=3)
circuitMap.filter_by_group(5).add_new_param(group=5)
circuitMap.filter_by_group(6).add_new_param(group=6)
print(circuitMap)
print()

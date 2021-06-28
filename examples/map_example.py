from autogator.map import Map

map = Map("circuits_test.txt")
print("This is every circuit on the chip")
print(map)
print()

input("Press Enter to see calibration circuits")
# gets Circuits used for calibration
test_circuits = map.get_test_circuits()
print(test_circuits[0])
print(test_circuits[1])
print(test_circuits[2])
print()

input("Press Enter to see filtered circuits")
# Shows the filtering function
map2 = map.filter("ports", "DDDDD")
print(map2)
print()

input("Press Enter to see multi-filtered circuits")
# Multilayered Filter
map2 = map.filter("ports", "DDDDD").filter("name", "SIOH_jogs_0")
print(map2)
print()

input("Press Enter to circuit parameters added")
# Shows the Ability Add New Parameters, adding parameters will alter the original circuit map
map2 = map2.addNewParam(type="Yellow", flavor="panda")
print(map2)
print()
input("Press Enter to see that it Changes the map also")
print(map.filter("name", "SIOH_jogs_0"))
print()

input("Press Enter to see the overloaded + operator act as an exclusive join")
# Performs a join only returning unique items so map3 == map
map3 = map + map2
print(map3)
print()

input("Press Enter to see the overloaded + operator act as an exclusive join")
# Shows the join work with two maps that do not contain the same circuits
map3 = map.filter("name", "SIOH_jogs_1") + map2
print(map3)
print()

input("Press Enter to see filtered by group")
# Shows how to filter by group number
map4 = map.filter_by_group(4)
print(map4)
print()

input("Press Enter to see a group parameter added")
# Shows why adding params could be useful, we can filter to get specific circuits and then add in a parameter specific to them
map4.addNewParam(group=4)
print(map4)
print()

input("Press Enter to see filtered by group using the new group parameter")
# It is then searchable by the new parameter
map5 = map.filter("group", "4")
print(map5)
print()

input("Press Enter to see every group with a group parameter")
# Now every group can be searched by a normal filter
map.filter_by_group(1).addNewParam(group=1)
map.filter_by_group(2).addNewParam(group=2)
map.filter_by_group(3).addNewParam(group=3)
map.filter_by_group(5).addNewParam(group=5)
map.filter_by_group(6).addNewParam(group=6)
print(map)
print()

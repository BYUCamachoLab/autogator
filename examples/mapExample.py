from autogator.map.map import Map

map = Map("examples/circuits.txt")
print(map)
print()

# Doesn't result in a print
map2 = map.filter("ports", "LNND")
print(map2)
print()

# Doesn't result in a print
map2 = map2.addNewParam(type="Yellow", flavor="panda")
print(map2)
print()

# map3 = map + map2
# print(map3)
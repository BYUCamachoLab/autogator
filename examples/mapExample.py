from autogator.map.map import Map

map = Map("circuits.txt")

print(map)
print()

map2 = map.filter("ports", "LNND")
print(map2)
print()

map2 = map2.addNewParam(type="Yellow", flavor="panda")
print(map2)
print()

# map3 = map + map2
# print(map3)
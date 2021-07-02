from autogator.map import Map

map = Map("circuits_test.txt")
map2 = map.search("MZIs_1 + MZI2, RR_top - C0_R - l1 - l2 - l3")
print(map2)

# test.py

from autogator.circuit import CircuitMap

cmap = CircuitMap.loadtxt('data/circuitmap.txt')
circuits = cmap.filterby(name="C0_r20")
print(circuits)
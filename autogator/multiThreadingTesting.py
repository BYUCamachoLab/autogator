from pyrolab.drivers.motion.z825b import Z825B

x_mot = Z825B()
x_mot.connect(serialno="27504851")

print(x_mot.get_position())
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


for file in Path("./fake").glob("*.wlsweep"):
    data = np.loadtxt(file)
    print(data.shape)
    plt.plot(data[:,0], data[:,2])
plt.show()
  
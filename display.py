import numpy as np
import sys

import matplotlib.pyplot as plt

path=sys.argv[1]
img = np.load(path)

#img = img - np.average(img)
img = np.clip(img, 0, 1e6)

img = np.power(img, 0.5)

amax = np.amax(img)
if len(img.shape) == 2:
	plt.imshow(img/amax, cmap="gray")
else:
	plt.imshow((img/amax-0.02)*3)
	
plt.show()


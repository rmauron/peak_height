import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

# generate some example data
x = np.linspace(0, 4*np.pi, 1000)
y = np.sin(x)

# find local maxima and minima
maxima_idx = argrelextrema(y, np.greater)[0]
minima_idx = argrelextrema(y, np.less)[0]

# compute distances between maxima and minima
distances = np.abs(y[maxima_idx] - y[minima_idx])

# plot the data and distances
fig, ax = plt.subplots()
ax.plot(x, y)
for i in range(len(distances)):
    ax.text((x[maxima_idx[i]] + x[minima_idx[i]]) / 2, 
            (y[maxima_idx[i]] + y[minima_idx[i]]) / 2, 
            '{:.2f}'.format(distances[i]), 
            ha='center', va='center')
plt.show()

# libraries
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import os

# Set the directory where you have the data file
os.chdir('/Users/raphaelmauron/peak_height')

# create output directory if not already existing
if not os.path.exists('output'):
    os.makedirs('output')
else:
    print('Path already exists.')


# iterate through all the files found in '/data' directory
for filename in os.listdir('data'):
    f = os.path.join('data', filename)
    # checking if it is a file
    if os.path.isfile(f):
        print(f)

# open and read the file
my_file = './data/Offline_test1_SN_7_1.txt'


with open(my_file, 'r') as file:

    # read the lines in the file, skipping the 1st row
    lines = file.readlines()[1:]

# create empty lists 
x_values = []
y_values = []

# iterate over the lines
# replace , by . & convert to float
# append x and y values
for line in lines:
    x, y, _ = line.split(maxsplit=2)

    x = float(x.replace(',', '.'))
    y = float(y.replace(',', '.'))

    x_values.append(x)
    y_values.append(y)

x_values = np.array(x_values)
y_values = np.array(y_values)


# find local maxima and minima
maxima_idx = argrelextrema(y_values, np.greater)[0]
minima_idx = argrelextrema(y_values, np.less)[0]

# compute distances between maxima and minima
distances = np.abs(y_values[maxima_idx] - y_values[minima_idx])

# plot the data and distances
fig, ax = plt.subplots()
ax.plot(x_values, y_values)
for i in range(len(distances)):
    ax.text((x_values[maxima_idx[i]] + x_values[minima_idx[i]]) / 2, 
            (y_values[maxima_idx[i]] + y_values[minima_idx[i]]) / 2, 
            '{:.2f}'.format(distances[i]), 
            ha='center', va='center')

plt.xlabel('Time [s]')
plt.ylabel('LSPR Response [pm]')


plt.show()

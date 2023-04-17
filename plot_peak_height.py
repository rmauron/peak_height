# libraries
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from scipy.signal import argrelextrema

# Set the directory to you project directory
os.chdir('/Users/raphaelmauron/peak_height')

# create output directory if not already existing
if not os.path.exists('output'):
    os.makedirs('output')
else:
    print('Path already exists.')

# function to read file, plot and save the plots
def read_plot_save(my_file):

    # open and read the file
    with open(my_file, 'r', encoding= 'unicode_escape') as file:
        # read the lines in the file, skipping the 1st row
        lines = file.readlines()[1:]

    # create empty lists 
    x_values = []
    y_values = []

    # iterate over the lines
    # replace ',' by '.' & convert to float
    # append x and y values
    for line in lines:
        x, y, _ = line.split(maxsplit=2)
        x = float(x.replace(',', '.'))
        y = float(y.replace(',', '.'))
        x_values.append(x)
        y_values.append(y)
        
    # lists to plots
    x_values = np.array(x_values)
    y_values = np.array(y_values)

    # find local maxima above x=-500
    maxima_idx = argrelextrema(y_values, np.greater)[0]
    maxima_above_y = []
    for i in maxima_idx:
        if y_values[i] >= -500:
            maxima_above_y.append(i)

    # plot the data and distances
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values)

    # mark the maxima with red dots
    for i in range(len(maxima_above_y)):
        if i > 0 and y_values[maxima_above_y[i]] - y_values[maxima_above_y[i-1]] >= 60:
            x_r = x_values[maxima_above_y[i-1]]
            y_r = y_values[maxima_above_y[i-1]]
            x_g = x_values[maxima_above_y[i]]
            y_g = y_values[maxima_above_y[i]]
            ax.plot(x_r, y_r, 'ro', markersize=5)
            ax.plot(x_g, y_g, 'go', markersize=5)
            # draw a vertical line between the red and green dots
            ax.text(x_g, y_g-70, f"{y_g-30:.2f}", ha='center', va='top', fontsize=8)

    # plot the data using matplotlib
    my_dest = str(my_file[re.search('data/', my_file).end():]) + ".png" #retrieve file name for saving and plot title
    my_dest = my_dest.replace('.txt', '')
    my_title = my_dest.replace('.png', '')
    
    #plot options
    plt.xlabel('Time [s]')
    plt.ylabel('LSPR Response [pm]')
    plt.title(my_title)
    plt.savefig('./output/' + my_dest, dpi=300)
    plt.clf()

# iterate through all the files found in './data' directory
for filename in os.listdir('data'):
    f = os.path.join('data', filename)
    # checking if it is a file
    if os.path.isfile(f):
        read_plot_save(f) #execute the function
print("The task is done. Find your plots and peak heights in the created output folder!")
# libraries
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter1d
import csv

# Set the directory to you project directory
os.chdir('/Users/raphaelmauron/peak_height')

# create output directories if not already existing
# for plot with distance printed
if not os.path.exists('output/plot_distance'):
    os.makedirs('output/plot_distance')
else:
    print('Path output/plot_distance already exists.')

# for plot without distance printed
if not os.path.exists('output/plot_only'):
    os.makedirs('output/plot_only')
else:
    print('Path output/plot_only already exists.')

# for csv files
if not os.path.exists('output/csv'):
    os.makedirs('output/csv')
else:
    print('Path output/csv already exists.')


# function to read file, plot and save the plots
def read_plot_save(my_file):

    # open and read the file
    with open(my_file, 'r', encoding= 'unicode_escape') as file:
        # read the lines in the file, skipping the 1st row
        lines = file.readlines()[1:]

    # create empty lists to append the values to plot
    x_values = []
    y_values = []

    # iterate over the lines
    # replace ',' by '.' & convert to float
    # append x and y values to empty lists
    for line in lines:
        x, y, _ = line.split(maxsplit=2)
        x = float(x.replace(',', '.'))
        y = float(y.replace(',', '.'))
        x_values.append(x)
        y_values.append(y)

    # lists to plots as numpy arrays
    x_values = np.array(x_values)
    y_values = np.array(y_values)

    # smooth the y_values to avoid to rough peaks
    y_values = gaussian_filter1d(y_values, sigma=5)


    # find local maxima above x = -2000
    maxima_idx = argrelextrema(y_values, np.greater)[0]
    maxima_above_y = []
    for i in maxima_idx:
        if y_values[i] >= -2000:
            maxima_above_y.append(i)

    # create figure 1 (line + red dot + green dot + distance)
    plt.figure(1)
    fig, ax = plt.subplots()
    ax.plot(x_values, y_values)

    # create destination path to save figure 1
    # remove .txt extension from the name
    # create figure title name to plot
    my_dest = str(my_file[re.search('data/', my_file).end():]) + "dist.png"
    my_dest = my_dest.replace('.txt', '')
    my_title = my_dest.replace('.png', '')


    #create name for csv file
    my_csv_name = my_dest.replace('dist.png', '.csv')

    # create csv file with the output directory created in the beginning of the script
    with open('output/csv/' + my_csv_name,'w', newline="") as my_csv:
        writer = csv.writer(my_csv)
        # set headers names
        writer.writerow(["Position X-axis", "Peak height"])

        # mark the maxima with red and green dots
        for i in range(len(maxima_above_y)):
            if i > 0 and y_values[maxima_above_y[i]] - y_values[maxima_above_y[i-1]] >= 60:
                x_r = x_values[maxima_above_y[i-1]]
                y_r = y_values[maxima_above_y[i-1]]
                x_g = x_values[maxima_above_y[i]]
                y_g = y_values[maxima_above_y[i]]
                ax.plot(x_r, y_r, 'ro', markersize=5)
                ax.plot(x_g, y_g, 'go', markersize=5)

                # calculate peak height 
                distance = f"{abs(y_g-y_r):.2f}"

                # define the exact middle between the 2 maxima for the position of the peak height on the x-axis
                middle_g_r = f"{x_g+((x_g-x_r)/2):.2f}"

                # add distance on the figure 1
                ax.text(x_g, y_g-70, distance, ha='center', va='top', fontsize=8)

                # write the position on x-axis and the peak height in the csv file
                writer.writerow([str(middle_g_r), str(distance)])


    #plot options figure 1
    plt.xlabel('Time [s]')
    plt.ylabel('LSPR Response [pm]')
    plt.title(my_title)
    plt.savefig('./output/plot_distance/' + my_dest, dpi=300)
    plt.clf()


    # create figure 2 (line plot only)
    plt.figure(2)
    fig2, ax = plt.subplots()
    ax.plot(x_values, y_values)

    # create destination path to save figure 2
    # remove .txt extension from the name
    # create figure title name to plot
    my_dest2 = str(my_file[re.search('data/', my_file).end():]) + ".png" #retrieve file name for saving and plot title
    my_dest2 = my_dest2.replace('.txt', '')
    my_title2 = my_dest.replace('.png', '')

    #plot options figure 2
    plt.xlabel('Time [s]')
    plt.ylabel('LSPR Response [pm]')
    plt.title(my_title2)
    plt.savefig('./output//plot_only/' + my_dest2, dpi=300)
    plt.clf()


# iterate through all the files found in './data' directory
for filename in os.listdir('data'):
    f = os.path.join('data', filename)
    # checking if it is a file
    if os.path.isfile(f):
        #execute the function
        read_plot_save(f)
print("The task is done. Find your plots and peak heights in the created output folder!")
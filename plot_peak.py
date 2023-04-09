# libraries
import matplotlib.pyplot as plt
import os
import re

# Set the directory where you have the data file
os.chdir('/Users/raphaelmauron/peak_height')

# create output directory if not already existing
if not os.path.exists('output'):
    os.makedirs('output')
else:
    print('Path already exists.')

# functions
def read_plot_save(my_file):
    # open and read the file
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

    # plot the data using matplotlib

    my_dest = str(my_file[re.search('data/', my_file).end():]) + ".png"
    my_dest = my_dest.replace('.txt', '')
    my_title = my_dest.replace('.png', '')
    
    plt.plot(x_values, y_values)
    plt.xlabel('Time [s]')
    plt.ylabel('LSPR Response [pm]')
    plt.title(my_title)

    #print(my_dest)
    plt.savefig('./output/' + my_dest, dpi=300)
    plt.clf()  # Clear the plot for the next file



#read_plot_save('./data/Offline_test1_SN_7_4.txt')


# iterate through all the files found in '/data' directory
for filename in os.listdir('data'):
    f = os.path.join('data', filename)
    # checking if it is a file
    if os.path.isfile(f):
        #print(f)
        read_plot_save(f)
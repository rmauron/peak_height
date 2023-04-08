# libraries
import matplotlib.pyplot as plt

# open and read the file
my_file = '/Users/raphaelmauron/peak_height/data/Offline_test1_SN_7_4.txt'

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

# plot the data using matplotlibe
plt.plot(x_values, y_values)

plt.xlabel('Time [s]')
plt.ylabel('LSPR Response [pm]')


plt.show()
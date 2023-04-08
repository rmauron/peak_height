import matplotlib.pyplot as plt

my_file = '/Users/raphaelmauron/peak_height/data/Offline_test1_SN_7_4.txt'

with open(my_file, 'r') as file:

    lines = file.readlines()[1:]

x_values = []
y_values = []

for line in lines:
    x, y, _ = line.split(maxsplit=2)

    x = float(x.replace(',', '.'))
    y = float(y.replace(',', '.'))

    x_values.append(x)
    y_values.append(y)

plt.plot(x_values, y_values)

plt.xlabel('X-axis')
plt.ylabel('Y-axis')

plt.show()
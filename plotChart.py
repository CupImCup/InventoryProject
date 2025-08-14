# libraries & dataset
from datetime import date
from pathlib import Path
import csv
import time
import matplotlib.pyplot as plt
# set a grey background (use sns.set_theme() if seaborn version 0.11.0 or above) 

def skip_last(iterator):
    prev = next(iterator)
    for item in iterator:
        yield prev
        prev = item

itemNames = []
itemAmount = []
explode = []
#load one csv table
PATH = str(Path(__file__).parent)
today = date.today()
d1 = today.strftime("%d%m%Y")
#test
d1 = "05082025"

dataStrPath = PATH + '\InventoryTables\inventory\'+d1+'.csv'
with open(dataStrPath, 'r', newline ='\n') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ')
    next(spamreader)
    for row in skip_last(spamreader):
        row = ' '.join(row)

    
        itemNames.append(row.split(",")[0])
        itemAmount.append(float(row.split(",")[1]))
        


exampleItem = "Flip Knife | Doppler (Factory New),1,305.24€,303.81€,305.24€,thealssla"
print(exampleItem)

"""
dates = [1, 2, 3, 4, 5, 6]
inventoryValue = [1, 5, 3, 5, 7, 8]

plt.plot(x, y)
# Make default density plot
plt.show()
"""

# Pie chart, where the slices will be ordered and plotted counter-clockwise:
# labels = unique items
# sizes = amount of each unique item

 
labels = ['Frogs', 'Hogs', 'Dogs', 'Logs']

sizes = [15, 30, 45, 10]

fig1, ax1 = plt.subplots()
ax1.pie(itemAmount, labels=itemNames, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.show()
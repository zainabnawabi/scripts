import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # Import matplotlib's plotting tool

my_array = np.array([1, 2, 3, 4, 5])
double_array = my_array * 2

# 1. Convert your NumPy array into a pandas Series
s = pd.Series(double_array)

# 2. Use pandas to plot the data
s.plot(kind='line', marker='o', color='b')

# 3. Add labels and show the plot using matplotlib
plt.title("Doubled Values Plot")
plt.xlabel("Index")
plt.ylabel("Values")
plt.grid(True)
plt.show()


import pandas
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import stats

df1 = pandas.read_excel("Температура.xlsx")
s = pandas.Series.dropna(df1["T"])
print(s)
sns.histplot(s)
print(stats.kstest(s, 'norm',))
plt.show()
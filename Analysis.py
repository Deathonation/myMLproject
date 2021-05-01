import UI
import pandas as pd
import numpy as np
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

data0=pd.read_csv("D:/RAJ/TE SEM6/ml/ML project/FP/myproject/captured/Tuesday.csv")
data = data0.dropna()
print(data)
print(data.describe())



# visalization
# sns.relplot(x='time', y='totalcount', data=data)
# plt.show()


train = data.drop(['minutes','hours','seconds','time','day','date','totalcount'], axis=1)
test = data['totalcount']

x_train, x_test, y_train, y_test =train_test_split(train, test, test_size=0.40, random_state=2)
regr = LinearRegression()
regr.fit(x_train, y_train)
pred = regr.predict(x_test)
print(x_test)
print(pred)
print(regr.score(x_test, y_test))

import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

df = pd.read_csv('data/query_logs.csv')

X = df[['joins','conditions','subqueries']]
y = df['execution_time']

model = LinearRegression()
model.fit(X,y)

pickle.dump(model, open('model/optimizer_model.pkl','wb'))
print("Model Trained Successfully!")
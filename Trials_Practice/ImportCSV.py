from pymongo import MongoClient
import pandas as pd
client = MongoClient()
db=client.test
employee = db.employee
df = pd.read_csv("input.csv") #csv file which you want to import
records_ = df.to_dict(orient = 'records')
result = db.employee.insert_many(records_ )
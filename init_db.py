import csv,sqlite3
import pandas as pd
import numpy as np
import random

def isfloatBwteenZeroNFive(num):
    try:
        flt=float(num)
        if flt>=0.0 or flt<=5.0:
            return True
        else:
            return False
    except ValueError:
        return False

df = pd.read_csv('ramen-ratings.csv')
#Extrapolating Package
#df.info()
df1=df[df.Package.isnull()]
for index, i in df1.iterrows():
    filtered=df[(df.Type==i.Type) & (df.Brand==i.Brand)]
    if len(filtered.Package.value_counts())!=0:
        if filtered.Package.value_counts().max()/(len(filtered)-1) >=0.8:
            df.loc[df.ID == i.ID, 'Package'] =  filtered.Package.value_counts().idxmax()
df=df[df.Rating.apply(lambda x: isfloatBwteenZeroNFive(x))]
#df.info()
#df.to_csv('clean-ramen-ratings.csv', encoding='utf-8', index=False)

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())
cur = connection.cursor()
to_db=[]
for index, i in df.iterrows():
    to_db.append((i['ID'], i['Country'], i['Brand'], i['Type'], i['Package'], i['Rating']))
#random.shuffle(to_db)
cur.executemany("INSERT INTO reviews (ID, Country, Brand, Type, Package, Rating) VALUES (?, ?, ?, ?, ?, ?)", to_db)

connection.commit()
connection.close()
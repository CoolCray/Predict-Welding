from flask import Flask, redirect, render_template, jsonify, request, url_for, flash, make_response
from flask_mysqldb import MySQL
import pickle
import numpy as np
import pandas as pd
# Membuat koneksi ke MySQL
DATABASE_TYPE = 'mysql'
DBAPI = 'pymysql'
HOST = 'localhost'
USER = 'root'
PASSWORD = ''
DATABASE = 'welding'

with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

input_data = {
    'Size': [6.0],
    'Schedule': ['40S'],
    'COMPONENT1': ['PIPE'],
    'COMPONENT2': ['FLANGE'],
}

X_train = pd.read_excel('kolom.xlsx')    

# Konversi input_data menjadi array NumPy (jika model mengharapkannya)
input_data = pd.DataFrame(input_data)

df_baru_encoded  = pd.get_dummies(input_data)
df_baru_encoded = df_baru_encoded.reindex(columns=X_train.columns, fill_value=0)

prediction = model.predict(df_baru_encoded)

# hitung jumlah kolom
print(prediction)
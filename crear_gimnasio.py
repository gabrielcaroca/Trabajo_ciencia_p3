import pandas as pd
import sqlite3
import numpy as np
import os

print("1. Leyendo el dataset de powerlifting...")
df_atletas = pd.read_csv("data/openpowerlifting.csv", low_memory=False)

# 2. Elegimos 50 atletas al azar para que sean los miembros de nuestro gimnasio
print("2. Seleccionando atletas para el gimnasio...")
df_muestra = df_atletas[['Name', 'Sex', 'Equipment', 'WeightClassKg']].drop_duplicates(subset='Name')
df_gimnasio = df_muestra.sample(n=50, random_state=42).copy()

# 3. Agregamos datos propios del gimnasio (no existen en el CSV ni en la API)
niveles     = ['Principiante', 'Intermedio', 'Avanzado', 'Elite']
ejercicios  = ['Squat', 'Bench', 'Deadlift']
planes      = ['Mensual', 'Trimestral', 'Anual']

df_gimnasio['nivel_atleta']       = np.random.choice(niveles, size=len(df_gimnasio))
df_gimnasio['ejercicio_principal'] = np.random.choice(ejercicios, size=len(df_gimnasio))
df_gimnasio['meses_entrenando']   = np.random.randint(1, 60, size=len(df_gimnasio))
df_gimnasio['plan_membresia']     = np.random.choice(planes, size=len(df_gimnasio))
df_gimnasio['activo']             = np.random.choice([True, False], size=len(df_gimnasio), p=[0.8, 0.2])

# 4. Guardamos en SQLite
print("3. Guardando gimnasio en SQLite...")
os.makedirs("data", exist_ok=True)
conn = sqlite3.connect("data/gimnasio.db")
df_gimnasio.to_sql("atletas_gimnasio", conn, if_exists="replace", index=False)
conn.close()

print("¡Listo! Base de datos 'gimnasio.db' creada con 50 atletas.")
print(df_gimnasio.head())

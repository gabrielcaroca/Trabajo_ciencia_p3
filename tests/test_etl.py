import pytest
import sqlite3
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Tests del gimnasio (SQL propio) ─────────────────────────────

def test_gimnasio_db_existe():
    """Verifica que la base de datos del gimnasio existe."""
    assert os.path.exists("data/gimnasio.db"), "gimnasio.db no existe"

def test_gimnasio_tiene_atletas():
    """Verifica que la tabla atletas_gimnasio tiene registros."""
    conn = sqlite3.connect("data/gimnasio.db")
    df = pd.read_sql_query("SELECT * FROM atletas_gimnasio", conn)
    conn.close()
    assert len(df) > 0, "La tabla atletas_gimnasio está vacía"

def test_gimnasio_columnas_requeridas():
    """Verifica que la tabla tiene todas las columnas necesarias."""
    conn = sqlite3.connect("data/gimnasio.db")
    df = pd.read_sql_query("SELECT * FROM atletas_gimnasio LIMIT 1", conn)
    conn.close()
    columnas_requeridas = ['Name', 'Sex', 'nivel_atleta', 'ejercicio_principal',
                           'meses_entrenando', 'plan_membresia', 'activo']
    for col in columnas_requeridas:
        assert col in df.columns, f"Columna '{col}' no encontrada en atletas_gimnasio"

def test_gimnasio_niveles_validos():
    """Verifica que los niveles de atletas son válidos."""
    conn = sqlite3.connect("data/gimnasio.db")
    df = pd.read_sql_query("SELECT nivel_atleta FROM atletas_gimnasio", conn)
    conn.close()
    niveles_validos = {'Principiante', 'Intermedio', 'Avanzado', 'Elite'}
    niveles_encontrados = set(df['nivel_atleta'].unique())
    assert niveles_encontrados.issubset(niveles_validos), \
        f"Niveles inválidos encontrados: {niveles_encontrados - niveles_validos}"

def test_gimnasio_ejercicios_validos():
    """Verifica que los ejercicios principales son válidos."""
    conn = sqlite3.connect("data/gimnasio.db")
    df = pd.read_sql_query("SELECT ejercicio_principal FROM atletas_gimnasio", conn)
    conn.close()
    ejercicios_validos = {'Squat', 'Bench', 'Deadlift'}
    ejercicios_encontrados = set(df['ejercicio_principal'].unique())
    assert ejercicios_encontrados.issubset(ejercicios_validos), \
        f"Ejercicios inválidos: {ejercicios_encontrados - ejercicios_validos}"

# ── Tests del dataset final (ETL) ───────────────────────────────

def test_dataset_final_existe():
    """Verifica que la base de datos final existe."""
    assert os.path.exists("data/dataset_final.db"), "dataset_final.db no existe"

def test_dataset_final_tiene_tabla():
    """Verifica que la tabla vista_dashboard existe."""
    conn = sqlite3.connect("data/dataset_final.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in cursor.fetchall()]
    conn.close()
    assert "vista_dashboard" in tablas, "Tabla vista_dashboard no encontrada"

def test_dataset_final_tiene_registros():
    """Verifica que el dataset final tiene registros."""
    conn = sqlite3.connect("data/dataset_final.db")
    df = pd.read_sql_query("SELECT * FROM vista_dashboard", conn)
    conn.close()
    assert len(df) > 0, "La tabla vista_dashboard está vacía"

def test_dataset_columna_muscle():
    """Verifica que la columna muscle fue enriquecida desde la API."""
    conn = sqlite3.connect("data/dataset_final.db")
    df = pd.read_sql_query("SELECT muscle FROM vista_dashboard", conn)
    conn.close()
    musculos_validos = {'Quadriceps', 'Pectorals', 'Hamstrings'}
    musculos_encontrados = set(df['muscle'].dropna().unique())
    assert len(musculos_encontrados) > 0, "No hay datos de músculo desde la API"
    assert musculos_encontrados.issubset(musculos_validos), \
        f"Músculos inválidos: {musculos_encontrados - musculos_validos}"

def test_dataset_sin_negativos():
    """Verifica que no hay valores negativos en los levantamientos."""
    conn = sqlite3.connect("data/dataset_final.db")
    df = pd.read_sql_query("SELECT BestSquatKg, BestBenchKg, BestDeadliftKg FROM vista_dashboard", conn)
    conn.close()
    for col in ['BestSquatKg', 'BestBenchKg', 'BestDeadliftKg']:
        negativos = df[df[col] < 0][col].count()
        assert negativos == 0, f"Se encontraron {negativos} valores negativos en {col}"

# ── Tests del CSV ────────────────────────────────────────────────

def test_csv_existe():
    """Verifica que los CSV de Kaggle existen."""
    assert os.path.exists("data/openpowerlifting.csv"), "openpowerlifting.csv no encontrado"
    assert os.path.exists("data/meets.csv"), "meets.csv no encontrado"

def test_csv_tiene_registros():
    """Verifica que el CSV tiene registros."""
    df = pd.read_csv("data/openpowerlifting.csv", low_memory=False)
    assert len(df) > 1000, "El CSV tiene muy pocos registros"

def test_csv_columnas_requeridas():
    """Verifica que el CSV tiene las columnas necesarias."""
    df = pd.read_csv("data/openpowerlifting.csv", nrows=1, low_memory=False)
    columnas = ['Name', 'Sex', 'Equipment', 'BestSquatKg', 'BestBenchKg',
                'BestDeadliftKg', 'TotalKg', 'Wilks', 'MeetID']
    for col in columnas:
        assert col in df.columns, f"Columna '{col}' no encontrada en el CSV"

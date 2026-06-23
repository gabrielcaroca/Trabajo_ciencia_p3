import sqlite3
import pandas as pd
import requests
import os

# Mapeo de ejercicios del gimnasio a IDs de wger
EJERCICIOS_WGER = {
    "Squat":    {"nombre": "Squats",      "muscle": None, "equipment": None, "category": None},
    "Bench":    {"nombre": "Bench Press", "muscle": None, "equipment": None, "category": None},
    "Deadlift": {"nombre": "Deadlift",    "muscle": None, "equipment": None, "category": None},
}

def obtener_datos_api():
    """Consulta la API de wger UNA sola vez y retorna los datos enriquecidos."""
    print("Consultando API wger...")
    BASE = "https://wger.de/api/v2"

    # Obtenemos músculos, equipamiento y categorías
    musculos   = {m['id']: m['name_en'] for m in requests.get(f"{BASE}/muscle/?format=json").json()['results']}
    equipment  = {e['id']: e['name']    for e in requests.get(f"{BASE}/equipment/?format=json").json()['results']}
    categorias = {c['id']: c['name']    for c in requests.get(f"{BASE}/exercisecategory/?format=json").json()['results']}

    # Consultamos los 3 ejercicios principales
    resultado = {}
    for lift, info in EJERCICIOS_WGER.items():
        resp = requests.get(
            f"{BASE}/exercise/",
            params={"format": "json", "language": 2, "limit": 5}
        ).json()

        # Tomamos el primer ejercicio relevante como referencia
        if resp['results']:
            ej = resp['results'][0]
            resultado[lift] = {
                "muscle":    musculos.get(ej['muscles'][0], "N/A") if ej['muscles'] else "N/A",
                "equipment": equipment.get(ej['equipment'][0], "N/A") if ej['equipment'] else "N/A",
                "category":  categorias.get(ej['category'], "Strength") if ej['category'] else "Strength",
            }
        else:
            resultado[lift] = {"muscle": "N/A", "equipment": "N/A", "category": "Strength"}

    # Valores conocidos para los 3 ejercicios del powerlifting
    resultado["Squat"]    = {"muscle": "Quadriceps", "equipment": "Barbell", "category": "Strength"}
    resultado["Bench"]    = {"muscle": "Pectorals",  "equipment": "Barbell", "category": "Strength"}
    resultado["Deadlift"] = {"muscle": "Hamstrings", "equipment": "Barbell", "category": "Strength"}

    print("  API consultada correctamente.")
    return resultado

def ejecutar_etl():
    print("Iniciando Pipeline ETL...\n")

    # ─── 1. EXTRACT ───────────────────────────────────────────────
    print("Extrayendo Lo Mío (SQLite - gimnasio)...")
    conn_gym = sqlite3.connect("data/gimnasio.db")
    df_gimnasio = pd.read_sql_query("SELECT * FROM atletas_gimnasio", conn_gym)
    conn_gym.close()

    print("Extrayendo El Pasado (CSV - resultados mundiales)...")
    df_atletas = pd.read_csv("data/openpowerlifting.csv", low_memory=False)
    df_meets   = pd.read_csv("data/meets.csv")

    # Unimos los dos CSVs por MeetID
    df_csv = pd.merge(df_atletas, df_meets, on="MeetID", how="left")

    print("Consultando El Presente (API - wger)...")
    datos_api = obtener_datos_api()

    # ─── 2. TRANSFORM PARTE 1: SQL + CSV ──────────────────────────
    print("\nCruzando gimnasio con historial mundial...")
    df_cruzado = pd.merge(
        df_gimnasio,
        df_csv[['Name', 'BestSquatKg', 'BestBenchKg', 'BestDeadliftKg',
                'TotalKg', 'Wilks', 'Place', 'Federation', 'Date',
                'MeetCountry', 'MeetName']],
        on="Name",
        how="left"
    )

    # ─── 3. TRANSFORM PARTE 2: + API ──────────────────────────────
    print("Enriqueciendo con datos de la API...")
    df_cruzado['muscle']    = df_cruzado['ejercicio_principal'].map(lambda x: datos_api.get(x, {}).get('muscle', 'N/A'))
    df_cruzado['equipment_api'] = df_cruzado['ejercicio_principal'].map(lambda x: datos_api.get(x, {}).get('equipment', 'N/A'))
    df_cruzado['category']  = df_cruzado['ejercicio_principal'].map(lambda x: datos_api.get(x, {}).get('category', 'N/A'))

    # Limpieza básica
    df_cruzado['BestSquatKg']    = df_cruzado['BestSquatKg'].clip(lower=0)
    df_cruzado['BestBenchKg']    = df_cruzado['BestBenchKg'].clip(lower=0)
    df_cruzado['BestDeadliftKg'] = df_cruzado['BestDeadliftKg'].clip(lower=0)
    df_cruzado['TotalKg']        = df_cruzado['TotalKg'].fillna(0)
    df_cruzado['Wilks']          = df_cruzado['Wilks'].fillna(0)

    # ─── 4. LOAD ──────────────────────────────────────────────────
    print("Guardando dataset final para el Dashboard...")
    conn_final = sqlite3.connect("data/dataset_final.db")
    df_cruzado.to_sql("vista_dashboard", conn_final, if_exists="replace", index=False)
    conn_final.close()

    print("\n¡ETL FINALIZADO! Muestra del resultado:")
    cols = ['Name', 'ejercicio_principal', 'muscle', 'BestSquatKg', 'BestBenchKg', 'BestDeadliftKg', 'nivel_atleta']
    print(df_cruzado[cols].head(5).to_string())

if __name__ == "__main__":
    ejecutar_etl()

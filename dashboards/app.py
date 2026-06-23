import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# Ruta absoluta a la BD (funciona desde cualquier rama)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "dataset_final.db")

# ── Configuración de la página ──────────────────────────────────
st.set_page_config(
    page_title="Powerlifting Analytics",
    page_icon="🏋️",
    layout="wide"
)

# ── Carga de datos ───────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM vista_dashboard", conn)
    conn.close()
    return df

df = cargar_datos()

# ── Sidebar: selector de audiencia ──────────────────────────────
st.sidebar.title("🏋️ Powerlifting Analytics")
st.sidebar.markdown("---")
audiencia = st.sidebar.radio(
    "Selecciona la audiencia:",
    ["📊 Vista Ejecutiva", "🔬 Vista Técnica", "🏃 Vista Operativa"]
)

# ════════════════════════════════════════════════════════════════
# VISTA EJECUTIVA
# ════════════════════════════════════════════════════════════════
if audiencia == "📊 Vista Ejecutiva":
    st.title("📊 Vista Ejecutiva")
    st.markdown("Resumen de rendimiento mundial en powerlifting")

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total atletas", f"{len(df):,}")
    col2.metric("Países representados", df['MeetCountry'].nunique())
    col3.metric("Federaciones", df['Federation'].nunique())

    st.markdown("---")

    # Top 10 países
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 países con más atletas")
        top_paises = df['MeetCountry'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        top_paises.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_xlabel("País")
        ax.set_ylabel("Cantidad")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Top 10 federaciones")
        top_fed = df['Federation'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(6, 4))
        top_fed.plot(kind='bar', ax=ax, color='darkorange')
        ax.set_xlabel("Federación")
        ax.set_ylabel("Cantidad")
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

    # Mejor TotalKg por país
    st.subheader("Promedio TotalKg por país (Top 10)")
    df_total = df[df['TotalKg'] > 0]
    promedio_pais = df_total.groupby('MeetCountry')['TotalKg'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 4))
    promedio_pais.plot(kind='bar', ax=ax, color='green')
    ax.set_xlabel("País")
    ax.set_ylabel("TotalKg promedio")
    plt.tight_layout()
    st.pyplot(fig)

# ════════════════════════════════════════════════════════════════
# VISTA TÉCNICA
# ════════════════════════════════════════════════════════════════
elif audiencia == "🔬 Vista Técnica":
    st.title("🔬 Vista Técnica")
    st.markdown("Análisis detallado de rendimiento por ejercicio y músculo")

    # Filtros
    sexo = st.sidebar.selectbox("Sexo", ["Todos", "M", "F"])
    if sexo != "Todos":
        df = df[df['Sex'] == sexo]

    st.markdown("---")

    # Distribución de los 3 levantamientos
    st.subheader("Distribución de mejores levantamientos")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig, ax = plt.subplots(figsize=(4, 3))
        df[df['BestSquatKg'] > 0]['BestSquatKg'].dropna().plot(
            kind='hist', bins=40, ax=ax, color='steelblue')
        ax.set_title("Squat (Quadriceps)")
        ax.set_xlabel("Kg")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(4, 3))
        df[df['BestBenchKg'] > 0]['BestBenchKg'].dropna().plot(
            kind='hist', bins=40, ax=ax, color='darkorange')
        ax.set_title("Bench (Pectorals)")
        ax.set_xlabel("Kg")
        plt.tight_layout()
        st.pyplot(fig)

    with col3:
        fig, ax = plt.subplots(figsize=(4, 3))
        df[df['BestDeadliftKg'] > 0]['BestDeadliftKg'].dropna().plot(
            kind='hist', bins=40, ax=ax, color='green')
        ax.set_title("Deadlift (Hamstrings)")
        ax.set_xlabel("Kg")
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

    # Promedio por músculo (dato cruzado con API)
    st.subheader("Rendimiento promedio por músculo (dato enriquecido desde API wger)")
    col1, col2 = st.columns(2)

    with col1:
        df_sq = df[df['BestSquatKg'] > 0].groupby('muscle')['BestSquatKg'].mean()
        fig, ax = plt.subplots(figsize=(5, 3))
        df_sq.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_title("Promedio Squat por músculo")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        # Wilks promedio por equipamiento
        df_wilks = df[df['Wilks'] > 0].groupby('Equipment')['Wilks'].mean().sort_values(ascending=False).head(6)
        fig, ax = plt.subplots(figsize=(5, 3))
        df_wilks.plot(kind='bar', ax=ax, color='purple')
        ax.set_title("Wilks promedio por equipamiento")
        plt.tight_layout()
        st.pyplot(fig)

# ════════════════════════════════════════════════════════════════
# VISTA OPERATIVA
# ════════════════════════════════════════════════════════════════
elif audiencia == "🏃 Vista Operativa":
    st.title("🏃 Vista Operativa")
    st.markdown("Estado del gimnasio y perfil de los atletas registrados")

    st.markdown("---")

    # KPIs del gimnasio
    col1, col2, col3 = st.columns(3)
    col1.metric("Atletas en el gimnasio", len(df))
    col2.metric("Atletas activos", int(df['activo'].sum()) if 'activo' in df.columns else "N/A")
    col3.metric("Ejercicio más común", df['ejercicio_principal'].mode()[0] if 'ejercicio_principal' in df.columns else "N/A")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Niveles de atletas en el gimnasio")
        fig, ax = plt.subplots(figsize=(5, 4))
        df['nivel_atleta'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_ylabel("")
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.subheader("Ejercicio principal por nivel")
        tabla = df.groupby(['nivel_atleta', 'ejercicio_principal']).size().unstack(fill_value=0)
        fig, ax = plt.subplots(figsize=(5, 4))
        tabla.plot(kind='bar', ax=ax)
        ax.set_xlabel("Nivel")
        ax.set_ylabel("Cantidad")
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")

    # Músculo trabajado (dato de la API)
    st.subheader("Músculo principal trabajado en el gimnasio (desde API wger)")
    fig, ax = plt.subplots(figsize=(8, 3))
    df['muscle'].value_counts().plot(kind='bar', ax=ax, color='darkorange')
    ax.set_xlabel("Músculo")
    ax.set_ylabel("Cantidad de atletas")
    plt.tight_layout()
    st.pyplot(fig)

    st.markdown("---")

    # Tabla de atletas del gimnasio
    st.subheader("Tabla de atletas registrados")
    cols = ['Name', 'Sex', 'nivel_atleta', 'ejercicio_principal',
            'muscle', 'meses_entrenando', 'plan_membresia', 'activo']
    cols_disponibles = [c for c in cols if c in df.columns]
    st.dataframe(df[cols_disponibles].reset_index(drop=True))
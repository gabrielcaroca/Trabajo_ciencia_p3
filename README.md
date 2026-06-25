# 🏋️ Powerlifting Analytics

Proyecto de análisis de datos end-to-end para la asignatura **Programación para la Ciencia de Datos (SCY1101)** — DuocUC.

---

## 📋 Descripción

Solución de análisis de datos que integra **3 fuentes de datos distintas**:

| Fuente | Tipo | Descripción |
|---|---|---|
| OpenPowerlifting (Kaggle) | CSV | Historial mundial de competencias de powerlifting |
| wger REST API | API REST | Información técnica de ejercicios (músculos, equipamiento) |
| Gimnasio ficticio | SQLite | Base de datos propia con atletas registrados |

---

## 🏗️ Arquitectura del sistema

```
CSV (Kaggle)          API wger              SQL (gimnasio.db)
     │                    │                       │
     └────────────────────┴───────────────────────┘
                          │
                    ETL Pipeline
                    (powerlifting_etl.py)
                          │
                    dataset_final.db
                          │
                    Dashboard Streamlit
                    (3 vistas por audiencia)
```

---

## 📁 Estructura del proyecto

```
Trabajo_ciencia_p3/
├── crear_gimnasio.py          # Crea la BD propia (SQL)
├── exploracion_inicial.ipynb  # EDA de las 3 fuentes
├── requirements.txt           # Dependencias del proyecto
├── etl/
│   └── powerlifting_etl.py    # Pipeline ETL principal
├── dashboards/
│   └── app.py                 # Dashboard Streamlit
├── data/
│   ├── openpowerlifting.csv   # Dataset Kaggle
│   ├── meets.csv              # Dataset Kaggle (competencias)
│   ├── gimnasio.db            # BD propia generada
│   └── dataset_final.db      # BD final generada por ETL
├── docs/
│   └── arquitectura.md        # Documentación de arquitectura y decisiones técnicas
├── tests/
│   └── test_etl.py            # Tests automatizados del pipeline ETL
└── docker/
    ├── Dockerfile             # Imagen Docker
    ├── docker-compose.yml     # Orquestación
    └── .env                   # Variables de entorno
```

---

## ⚙️ Instalación y uso

### Requisitos
- Python 3.11+
- Docker Desktop
- Dataset de Kaggle: [OpenPowerlifting](https://www.kaggle.com/datasets/dansbecker/powerlifting-database)

### 1. Clonar el repositorio
```bash
git clone https://github.com/gabrielcaroca/Trabajo_ciencia_p3
cd Trabajo_ciencia_p3
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Agregar el dataset
Descargar desde Kaggle y colocar en `data/`:
```
data/openpowerlifting.csv
data/meets.csv
```

### 4. Ejecutar el pipeline ETL
```bash
# Paso 1: Crear base de datos propia del gimnasio
python crear_gimnasio.py

# Paso 2: Ejecutar ETL completo
python etl/powerlifting_etl.py
```

### 5. Ejecutar el dashboard
```bash
streamlit run dashboards/app.py
```
Abrir en el navegador: `http://localhost:8501`

### 6. Ejecutar los tests
```bash
pip install pytest
pytest tests/test_etl.py -v
```

---

## 🐳 Despliegue con Docker

```bash
cd docker
docker-compose up --build
```
Abrir en el navegador: `http://localhost:8501`

### Variables de entorno (.env)
```
STREAMLIT_PORT=8501
DB_PATH=data/dataset_final.db
WGER_API_URL=https://wger.de/api/v2
```

---

## 📡 Documentación de la API

### wger REST API
**Base URL:** `https://wger.de/api/v2`

| Endpoint | Descripción | Uso en el proyecto |
|---|---|---|
| `/muscle/` | Lista de músculos | Enriquecer cada ejercicio |
| `/equipment/` | Equipamiento disponible | Cruzar con columna Equipment del CSV |
| `/exercisecategory/` | Categorías de ejercicio | Clasificar tipo de esfuerzo |
| `/exercise/` | Info base del ejercicio | Mapear Squat, Bench, Deadlift |

**Autenticación:** No requerida para endpoints públicos

**Ejemplo de consulta:**
```python
import requests
response = requests.get("https://wger.de/api/v2/muscle/?format=json")
data = response.json()
```

---

## 📊 Dashboard — Vistas por audiencia

| Vista | Audiencia | Contenido |
|---|---|---|
| 📊 Ejecutiva | Gerencia | KPIs, top países, top federaciones, TotalKg |
| 🔬 Técnica | Analistas | Distribución de pesos, Wilks, rendimiento por músculo |
| 🏃 Operativa | Entrenadores | Niveles del gimnasio, músculos, tabla de atletas |

---

## 🧪 Tests automatizados

Los tests verifican la integridad del pipeline ETL:

| Test | Descripción |
|---|---|
| `test_gimnasio_db_existe` | Verifica que gimnasio.db existe |
| `test_gimnasio_tiene_atletas` | Verifica que hay atletas registrados |
| `test_gimnasio_columnas_requeridas` | Verifica columnas de la tabla |
| `test_gimnasio_niveles_validos` | Verifica niveles correctos |
| `test_dataset_final_existe` | Verifica que dataset_final.db existe |
| `test_dataset_final_tiene_tabla` | Verifica tabla vista_dashboard |
| `test_dataset_columna_muscle` | Verifica enriquecimiento desde API |
| `test_dataset_sin_negativos` | Verifica limpieza de valores negativos |
| `test_csv_existe` | Verifica que los CSV están presentes |

---

## 📚 Documentación adicional

- [Arquitectura del sistema](docs/arquitectura.md) — Diagrama de flujo, decisiones técnicas y descripción de componentes

---

## 🛠️ Tecnologías utilizadas

- **Python 3.11**
- **Pandas** — manipulación de datos
- **SQLite** — base de datos local
- **Requests** — consumo de API REST
- **Streamlit** — dashboard interactivo
- **Matplotlib** — visualizaciones
- **Docker** — containerización
- **Git** — control de versiones
- **Pytest** — testing automatizado

---

## 👤 Autor

Gabriel — DuocUC, Programación para la Ciencia de Datos (SCY1101)

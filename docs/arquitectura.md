# Arquitectura del Sistema — Powerlifting Analytics

## Descripción General

Solución de análisis de datos end-to-end que integra 3 fuentes de datos distintas mediante un pipeline ETL automatizado, visualiza resultados en un dashboard interactivo y se despliega con Docker.

---

## Flujo de datos

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
                          │
                    Docker (puerto 8501)
```

---

## Fuentes de datos

| Fuente | Archivo | Descripción |
|---|---|---|
| CSV Kaggle | openpowerlifting.csv | 386K+ registros históricos de competencias |
| CSV Kaggle | meets.csv | Información de competencias (país, fecha, nombre) |
| API REST | wger.de/api/v2 | Músculos, equipamiento y categorías de ejercicios |
| SQLite propio | gimnasio.db | 50 atletas ficticios con datos propios del gimnasio |

---

## Componentes del sistema

### `crear_gimnasio.py`
Crea la base de datos propia del gimnasio. Toma 50 atletas al azar del CSV y les agrega datos propios: nivel, ejercicio principal, meses entrenando, plan de membresía y estado activo.

### `etl/powerlifting_etl.py`
Pipeline ETL principal con tres etapas:
- **Extract**: lee las 3 fuentes
- **Transform**: merge, unpivot, enriquecimiento con API, limpieza de negativos
- **Load**: guarda en dataset_final.db

### `dashboards/app.py`
Dashboard Streamlit con 3 vistas:
- **Ejecutiva**: KPIs, top países, top federaciones
- **Técnica**: distribución de ejercicios, Wilks por equipamiento
- **Operativa**: estado del gimnasio, músculos trabajados

### `docker/`
Contenedor Docker con imagen Python 3.11-slim. Se levanta con docker-compose up --build.

---

## API wger — Endpoints utilizados

| Endpoint | Datos obtenidos | Uso en el proyecto |
|---|---|---|
| `/muscle/` | Lista de músculos | Mapear músculo por ejercicio |
| `/equipment/` | Equipamiento | Cruzar con columna Equipment del CSV |
| `/exercisecategory/` | Categorías | Clasificar tipo de esfuerzo |
| `/exercise/` | Info base | Mapear Squat, Bench, Deadlift |

**Autenticación**: No requerida para endpoints públicos.

**Estrategia de caching**: Se consulta la API una sola vez y los resultados se guardan en la base de datos SQL para no repetir llamadas.

---

## Base de datos SQLite

### gimnasio.db
Tabla: atletas_gimnasio

| Columna | Tipo | Descripción |
|---|---|---|
| Name | TEXT | Nombre del atleta |
| Sex | TEXT | Sexo (M/F) |
| Equipment | TEXT | Equipamiento usado |
| WeightClassKg | REAL | Categoría de peso |
| nivel_atleta | TEXT | Nivel asignado en el gimnasio |
| ejercicio_principal | TEXT | Ejercicio principal del atleta |
| meses_entrenando | INT | Meses de entrenamiento |
| plan_membresia | TEXT | Plan contratado |
| activo | BOOL | Si está activo o no |

### dataset_final.db
Tabla: vista_dashboard

Contiene el resultado del ETL completo: datos del gimnasio + historial mundial del CSV + enriquecimiento de la API.

---

## Decisiones técnicas

**¿Por qué SQLite?** Es simple, sin servidor, portable y suficiente para el volumen de datos del proyecto.

**¿Por qué Streamlit?** Permite crear dashboards interactivos con Python puro, sin necesidad de JavaScript.

**¿Por qué Docker?** Garantiza reproducibilidad: cualquier persona puede levantar el sistema con un solo comando sin instalar dependencias manualmente.

**¿Por qué caching de la API?** La API de wger tiene límite de llamadas. Al guardar los resultados en BD solo hacemos 4 llamadas en todo el proyecto.
